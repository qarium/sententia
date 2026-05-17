from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from ..storage import Storage


def _clean_markdown(text: str) -> str:
    """Remove code blocks, images, and normalize whitespace."""
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"#{1,6}\s+", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_text(text: str, size: int = 600, overlap: int = 60) -> list[str]:
    """Split text into chunks of approximately `size` characters with `overlap`."""
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + size
        if end >= len(text):
            chunks.append(text[start:])
            break
        break_point = text.rfind("\n", end - size // 5, end)
        if break_point == -1:
            break_point = end
        chunks.append(text[start:break_point])
        start = max(break_point - overlap, start + 1)
    return [c.strip() for c in chunks if c.strip()]


class Index:
    """Semantic index over Markdown files using FAISS and sentence-transformers."""

    def __init__(self, storage: Storage, index_path: str | None = None, default_top: int = 10) -> None:
        self.storage = storage
        self.index_path = index_path
        self.default_top = default_top
        self.embedder = SentenceTransformer("intfloat/multilingual-e5-base")
        self.index: faiss.IndexFlatIP | None = None
        self.chunks: list[dict[str, str]] = []

        if index_path is not None and not index_path:
            raise ValueError("index_path must be a non-empty string or None")

        if index_path is None:
            self.index_directory()
        elif Path(index_path).exists():
            loaded = self.load()
            if not loaded:
                self.index_directory()
                self.save()
        else:
            self.index_directory()
            self.save()

    def index_directory(self) -> dict[str, Any]:
        """Build index from files provided by Storage."""
        files = self.storage.list_files()

        chunks: list[dict[str, str]] = []
        for file_path in files:
            content = self.storage.read_file(file_path)
            cleaned = _clean_markdown(content["text"])
            file_chunks = _split_text(cleaned)
            for c in file_chunks:
                chunks.append({"text": c, "source": content["source"]})

        if not chunks:
            probe = self.embedder.encode(["probe"])
            dim = probe.shape[1]
            self.index = faiss.IndexFlatIP(dim)
            self.chunks = []
            return {"files": len(files), "chunks": 0, "dimensions": dim}

        texts = ["passage: " + c["text"] for c in chunks]
        embeddings = self.embedder.encode(texts)
        dim = embeddings.shape[1]
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        embeddings = embeddings / norms

        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings.astype("float32"))
        self.chunks = chunks
        return {"files": len(files), "chunks": len(chunks), "dimensions": dim}

    def search(self, query: str, top: int | None = None) -> list[dict[str, Any]]:
        """Search the index for chunks most similar to the query."""
        if self.index is None or not self.chunks:
            return []

        top_k = top if top is not None else self.default_top
        q_embedding = self.embedder.encode(["query: " + query])
        q_norms = np.linalg.norm(q_embedding, axis=1, keepdims=True)
        q_norms[q_norms == 0] = 1.0
        q_embedding = q_embedding / q_norms

        distances, indices = self.index.search(q_embedding.astype("float32"), top_k)
        results: list[dict[str, Any]] = []
        for i in range(top_k):
            idx = indices[0][i]
            if idx < 0 or idx >= len(self.chunks):
                break
            results.append(
                {
                    "text": self.chunks[idx]["text"],
                    "source": self.chunks[idx]["source"],
                    "score": float(distances[0][i]),
                }
            )
        return results

    def save(self) -> None:
        """Serialize FAISS index and chunk metadata to disk."""
        if self.index_path is None:
            raise ValueError("Cannot save: index is in in-memory mode")
        if self.index is None:
            return
        Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        meta_path = self.index_path + ".meta"
        Path(meta_path).write_text(json.dumps(self.chunks, ensure_ascii=False), encoding="utf-8")

    def load(self) -> bool:
        """Deserialize FAISS index and chunk metadata from disk."""
        if self.index_path is None:
            raise ValueError("Cannot load: index is in in-memory mode")
        meta_path = self.index_path + ".meta"
        if not Path(self.index_path).exists() or not Path(meta_path).exists():
            return False
        try:
            self.index = faiss.read_index(self.index_path)
            self.chunks = json.loads(Path(meta_path).read_text(encoding="utf-8"))
            if not isinstance(self.chunks, list):
                return False
            return self.index.ntotal == len(self.chunks)
        except (OSError, RuntimeError, ValueError, TypeError):
            return False
