from __future__ import annotations

from pathlib import Path

import pytest
from sententia.index import Index
from sententia.storage import Storage


@pytest.fixture
def storage_with_files(tmp_path: Path) -> Storage:
    """Storage with 2 .md files for in-memory testing."""
    (tmp_path / "alpha.md").write_text("# Alpha\nThis is the alpha document with some content.", encoding="utf-8")
    (tmp_path / "beta.md").write_text("# Beta\nThis is the beta document with other content.", encoding="utf-8")
    return Storage(str(tmp_path))


@pytest.fixture
def empty_storage(tmp_path: Path) -> Storage:
    """Storage pointing to an empty directory."""
    return Storage(str(tmp_path))


@pytest.fixture
def in_memory_index(storage_with_files: Storage) -> Index:
    """In-memory Index built from Storage without index_path."""
    return Index(storage_with_files)


def test_index_in_memory_builds_from_storage(in_memory_index: Index) -> None:
    assert in_memory_index.index is not None
    assert len(in_memory_index.chunks) >= 2
    assert in_memory_index.index_path is None
    assert in_memory_index.index.ntotal == len(in_memory_index.chunks)


def test_index_in_memory_search_works(in_memory_index: Index) -> None:
    results = in_memory_index.search("content")
    assert len(results) > 0
    for r in results:
        assert "text" in r
        assert "source" in r
        assert "score" in r
        assert r["score"] > 0


def test_index_in_memory_save_raises(in_memory_index: Index) -> None:
    with pytest.raises(ValueError, match="in-memory"):
        in_memory_index.save()


def test_index_in_memory_load_raises(in_memory_index: Index) -> None:
    with pytest.raises(ValueError, match="in-memory"):
        in_memory_index.load()


def test_index_persistent_mode_unchanged(storage_with_files: Storage, tmp_path: Path) -> None:
    index_file = tmp_path / "test.faiss"
    index = Index(storage_with_files, str(index_file))
    assert index.index_path == str(index_file)
    assert Path(index_file).exists()


def test_index_in_memory_empty_directory(empty_storage: Storage) -> None:
    index = Index(empty_storage)
    assert index.index is not None
    assert len(index.chunks) == 0
    assert index.index.ntotal == 0
