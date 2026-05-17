"""Shared test fixtures and mock setup."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np


class MockFaissIndex:
    """Mock FAISS index that simulates search behavior."""

    def __init__(self, dim: int) -> None:
        self.dim = dim
        self._vectors: list[np.ndarray] = []
        self.ntotal = 0

    def add(self, vectors: np.ndarray) -> None:
        self._vectors = list(vectors)
        self.ntotal = len(self._vectors)

    def search(self, query: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
        n = len(self._vectors)
        distances = np.full((1, k), -1.0, dtype=np.float32)
        indices = np.full((1, k), -1, dtype=np.int64)
        for i in range(min(k, n)):
            distances[0][i] = 1.0
            indices[0][i] = i
        return distances, indices


class MockFaissModule:
    IndexFlatIP = MockFaissIndex

    @staticmethod
    def write_index(index: object, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(str(index.ntotal), encoding="utf-8")

    @staticmethod
    def read_index(path: str) -> object:
        try:
            ntotal = int(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            ntotal = 0
        idx = MockFaissIndex(768)
        idx.ntotal = ntotal
        # Populate _vectors so search() works after load
        idx._vectors = [np.zeros(768, dtype=np.float32) for _ in range(ntotal)]
        return idx


# Install mocks before any test module imports sententia packages
if "faiss" not in sys.modules:
    sys.modules["faiss"] = MockFaissModule()

if "sentence_transformers" not in sys.modules:
    _st_mock = MagicMock()
    sys.modules["sentence_transformers"] = _st_mock


def _encode_side_effect(texts, *args, **kwargs):
    n = len(texts) if isinstance(texts, list) else 1
    return np.random.rand(n, 768).astype(np.float32)


_st_mock = sys.modules["sentence_transformers"]
_st_mock.SentenceTransformer.return_value.encode.side_effect = _encode_side_effect
