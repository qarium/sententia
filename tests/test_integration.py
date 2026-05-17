"""Integration tests: cross-cell scenarios covering the full pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from fastapi import HTTPException
from sententia.api import AskResource, FilesResource, SearchResource
from sententia.api.files import FileResponse
from sententia.api.search import SearchRequest, SearchResponse
from sententia.app import SententiaApp
from sententia.endpoints import RESTResource
from sententia.rag import ask
from sententia.storage import Storage


def _make_mock_embedder() -> MagicMock:
    """Create a mock embedder whose encode() returns deterministic normalized vectors."""
    embedder = MagicMock()

    def encode(texts: list[str], **_kwargs: object) -> np.ndarray:
        n = len(texts)
        rng = np.random.RandomState(42)
        vectors = rng.randn(n, 768).astype(np.float32)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        vectors = vectors / norms
        return vectors

    embedder.encode = MagicMock(side_effect=encode)
    return embedder


@pytest.fixture
def data_dir(tmp_path: Path) -> str:
    """Create sample markdown files for integration tests."""
    (tmp_path / "python.md").write_text(
        "# Python\n\nPython — это язык программирования.\nОн поддерживает классы и функции.\n",
        encoding="utf-8",
    )
    (tmp_path / "rust.md").write_text(
        "# Rust\n\nRust — системный язык программирования.\nБезопасность памяти — его ключевая особенность.\n",
        encoding="utf-8",
    )
    return str(tmp_path)


@pytest.fixture
def mock_embedder() -> MagicMock:
    return _make_mock_embedder()


class TestStorageToFilesResource:
    """Storage → FilesResource: real filesystem integration."""

    def test_integration_storage_to_files_resource(self, tmp_path: Path) -> None:
        """Real Storage + FilesResource → get('test.md') → FileResponse with correct data."""
        (tmp_path / "test.md").write_text("# Hello\n\nContent here.", encoding="utf-8")
        storage = Storage(str(tmp_path))
        resource = FilesResource(storage)

        response = resource.get(path="test.md")
        assert isinstance(response, FileResponse)
        assert response.text == "# Hello\n\nContent here."
        assert response.source == "test.md"

    def test_files_read_from_subdirectory(self, tmp_path: Path) -> None:
        """Storage with nested directory → FilesResource returns correct source path."""
        sub = tmp_path / "docs"
        sub.mkdir()
        (sub / "guide.md").write_text("Guide content", encoding="utf-8")
        storage = Storage(str(tmp_path))
        resource = FilesResource(storage)

        response = resource.get(path="docs/guide.md")
        assert isinstance(response, FileResponse)
        assert response.text == "Guide content"
        assert response.source == "docs/guide.md"

    def test_files_path_traversal_blocked(self, tmp_path: Path) -> None:
        """Storage + FilesResource → path traversal → HTTPException 404."""
        storage = Storage(str(tmp_path))
        resource = FilesResource(storage)

        with pytest.raises(HTTPException) as exc_info:
            resource.get(path="../../etc/passwd")
        assert exc_info.value.status_code == 404

    def test_files_not_found(self, tmp_path: Path) -> None:
        """Storage + FilesResource → missing file → HTTPException 404."""
        storage = Storage(str(tmp_path))
        resource = FilesResource(storage)

        with pytest.raises(HTTPException, match="File not found"):
            resource.get(path="missing.md")


class TestIndexToSearchResource:
    """Index → SearchResource: real Index + mock embedder → verify response format."""

    @patch("sententia.index.indexer.SentenceTransformer")
    def test_integration_index_to_search_resource(
        self, mock_st_cls: MagicMock, data_dir: str, tmp_path: Path, mock_embedder: MagicMock
    ) -> None:
        """Real Index(Storage(data_dir), index_path) + SearchResource → post(SearchRequest) → SearchResponse."""
        from sententia.index import Index  # noqa: PLC0415

        mock_st_cls.return_value = mock_embedder
        index_path = str(tmp_path / "search-pipeline.index")

        idx = Index(Storage(data_dir), index_path)
        resource = SearchResource(idx)

        request = SearchRequest(query="Python", top=3)
        response = resource.post(request)

        assert isinstance(response, SearchResponse)
        for item in response.results:
            assert hasattr(item, "text")
            assert hasattr(item, "source")
            assert hasattr(item, "score")
            assert isinstance(item.score, float)
            assert isinstance(item.text, str)
            assert isinstance(item.source, str)

    @patch("sententia.index.indexer.SentenceTransformer")
    def test_search_resource_passes_query_and_top(
        self, mock_st_cls: MagicMock, data_dir: str, tmp_path: Path, mock_embedder: MagicMock
    ) -> None:
        from sententia.index import Index  # noqa: PLC0415

        mock_st_cls.return_value = mock_embedder
        index_path = str(tmp_path / "search-args.index")

        idx = Index(Storage(data_dir), index_path)
        resource = SearchResource(idx)

        request = SearchRequest(query="Rust", top=2)
        response = resource.post(request)

        assert isinstance(response, SearchResponse)
        assert len(response.results) <= 2


class TestRagPipeline:
    """Mock Index + mock LLMProvider + ask() → verify response and prompt content."""

    def test_integration_rag_pipeline(self) -> None:
        """mock Index + mock LLMProvider + ask() → answer with sources, prompt contains 'Недостаточно данных'."""
        mock_index = MagicMock()
        mock_index.search.return_value = [
            {"text": "Python — язык программирования", "source": "python.md", "score": 0.9},
        ]
        mock_llm = MagicMock()

        captured_prompt: str | None = None

        def capture_generate(prompt: str) -> str:
            nonlocal captured_prompt
            captured_prompt = prompt
            return "Python — это язык программирования."

        mock_llm.generate.side_effect = capture_generate

        result = ask("Что такое Python?", mock_index, mock_llm, top=3)
        assert result["answer"] == "Python — это язык программирования."
        assert result["sources"] == ["python.md"]
        assert captured_prompt is not None
        assert "Недостаточно данных" in captured_prompt

    def test_ask_pipeline_unique_sources(self) -> None:
        """ask() deduplicates sources from search results."""
        mock_index = MagicMock()
        mock_index.search.return_value = [
            {"text": "chunk1", "source": "python.md", "score": 0.9},
            {"text": "chunk2", "source": "python.md", "score": 0.8},
            {"text": "chunk3", "source": "rust.md", "score": 0.7},
        ]
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Ответ"

        result = ask("query", mock_index, mock_llm, top=3)
        assert result["sources"] == ["python.md", "rust.md"]

    def test_ask_empty_search_results(self) -> None:
        """Empty index search → sources == [], LLM returns 'Недостаточно данных'."""
        mock_index = MagicMock()
        mock_index.search.return_value = []
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Недостаточно данных для ответа на данный вопрос"

        result = ask("something", mock_index, mock_llm, top=3)
        assert result["sources"] == []
        assert result["answer"] == "Недостаточно данных для ответа на данный вопрос"


class TestFullAssembly:
    """Monkeypatch all components → main() → SententiaApp created, resources registered."""

    def test_integration_full_assembly(self, tmp_path: Path) -> None:
        """main() with all components monkeypatched → SententiaApp created, 3 routes registered."""
        from sententia.__main__ import main  # noqa: PLC0415
        from sententia.storage import Storage as StorageClass  # noqa: PLC0415

        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "test.md").write_text("# Test\n\nHello.", encoding="utf-8")

        created_components: dict[str, object] = {}

        real_storage = StorageClass(str(data_dir))

        def mock_storage_init(directory_path: str) -> StorageClass:
            created_components["storage_dir"] = directory_path
            return real_storage

        with (
            patch("sententia.index.indexer.SentenceTransformer") as mock_st_cls,
            patch("sententia.storage.Storage", side_effect=mock_storage_init),
            patch("sententia.llm.OpenaiProvider") as mock_openai_cls,
            patch("sententia.app.app.uvicorn.run") as mock_run,
        ):
            mock_st_cls.return_value.encode.side_effect = lambda texts, *_a, **_kw: np.random.rand(
                len(texts) if isinstance(texts, list) else 1, 768
            ).astype(np.float32)
            main(
                [
                    str(data_dir),
                    "--llm-protocol",
                    "ollama",
                    "--llm-url",
                    "http://localhost:11434",
                    "--llm-model",
                    "llama3",
                ]
            )

        assert created_components["storage_dir"] == str(data_dir)
        mock_openai_cls.assert_called_once_with("http://localhost:11434", "llama3", None)
        mock_run.assert_called_once()

        # Verify uvicorn.run was called with a FastAPI app that has all 3 routes
        call_args = mock_run.call_args
        app = call_args[0][0]
        routes = [r.path for r in app.routes]
        assert "/search" in routes
        assert "/ask" in routes
        assert "/files/{path:path}" in routes


class TestSententiaAppRegistration:
    """SententiaApp: create + register all 3 resources → verify routes exist."""

    @patch("sententia.index.indexer.SentenceTransformer")
    def test_app_registers_all_resources(
        self, mock_st_cls: MagicMock, data_dir: str, tmp_path: Path, mock_embedder: MagicMock
    ) -> None:
        from sententia.index import Index  # noqa: PLC0415

        mock_st_cls.return_value = mock_embedder
        index_path = str(tmp_path / "app.index")

        storage = Storage(data_dir)
        idx = Index(storage, index_path)
        mock_llm = MagicMock()

        search_res = SearchResource(idx)
        ask_res = AskResource(idx, mock_llm)
        files_res = FilesResource(storage)

        app = SententiaApp()
        app.add_rest_resource(search_res)
        app.add_rest_resource(ask_res)
        app.add_rest_resource(files_res)

        routes = [r.path for r in app._app.routes]
        assert "/search" in routes
        assert "/ask" in routes
        assert "/files/{path:path}" in routes

    @patch("sententia.index.indexer.SentenceTransformer")
    def test_app_resources_are_restresource_subclasses(
        self, mock_st_cls: MagicMock, data_dir: str, tmp_path: Path, mock_embedder: MagicMock
    ) -> None:
        from sententia.index import Index  # noqa: PLC0415

        mock_st_cls.return_value = mock_embedder
        index_path = str(tmp_path / "app-subclass.index")

        storage = Storage(data_dir)
        idx = Index(storage, index_path)
        mock_llm = MagicMock()

        resources: list[RESTResource] = [
            SearchResource(idx),
            AskResource(idx, mock_llm),
            FilesResource(storage),
        ]

        for res in resources:
            assert isinstance(res, RESTResource)
            assert isinstance(res.url_rule, str)


class TestSaveLoadPersistence:
    """Index: build → save → load → search yields same results."""

    @patch("sententia.index.indexer.SentenceTransformer")
    def test_save_load_search_consistency(
        self, mock_st_cls: MagicMock, data_dir: str, tmp_path: Path, mock_embedder: MagicMock
    ) -> None:
        from sententia.index import Index  # noqa: PLC0415

        mock_st_cls.return_value = mock_embedder
        index_path = str(tmp_path / "persist.index")

        # First instance: build, search, save
        idx1 = Index(Storage(data_dir), index_path)
        results1 = idx1.search("Python", top=5)
        assert len(results1) > 0

        # Second instance: load from disk
        idx2 = Index(Storage(data_dir), index_path)
        assert len(idx2.chunks) == len(idx1.chunks)

        results2 = idx2.search("Python", top=5)
        assert len(results2) == len(results1)

        # Verify chunk texts match
        for r1, r2 in zip(results1, results2, strict=True):
            assert r1["text"] == r2["text"]
            assert r1["source"] == r2["source"]

    @patch("sententia.index.indexer.SentenceTransformer")
    def test_load_corrupted_index_falls_back_to_rebuild(
        self, mock_st_cls: MagicMock, data_dir: str, tmp_path: Path, mock_embedder: MagicMock
    ) -> None:
        from sententia.index import Index  # noqa: PLC0415

        mock_st_cls.return_value = mock_embedder
        index_path = str(tmp_path / "corrupt.index")

        # Build a valid index
        idx1 = Index(Storage(data_dir), index_path)
        original_chunks = len(idx1.chunks)

        # Corrupt the index file
        Path(index_path).write_bytes(b"garbage data that is not a valid faiss index")

        # Reload — should fall back to rebuild
        idx2 = Index(Storage(data_dir), index_path)
        assert len(idx2.chunks) == original_chunks
