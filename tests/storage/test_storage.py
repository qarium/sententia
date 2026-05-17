from __future__ import annotations

from pathlib import Path

import pytest
from sententia.storage import Storage

# --- Contract tests ---


class TestStorageContract:
    """Contract tests: verify Storage facade, constructor, and method signatures."""

    def test_storage_importable(self) -> None:
        assert Storage is not None

    def test_storage_constructor_signature(self) -> None:
        storage = Storage("/some/path")
        assert isinstance(storage, Storage)
        assert hasattr(storage, "_base")
        assert isinstance(storage._base, Path)

    def test_storage_has_read_file(self) -> None:
        storage = Storage("/some/path")
        assert callable(getattr(storage, "read_file", None))

    def test_storage_has_list_files(self) -> None:
        storage = Storage("/some/path")
        assert callable(getattr(storage, "list_files", None))

    def test_storage_list_files_returns_list(self) -> None:
        storage = Storage("/some/path")
        result = storage.list_files()
        assert isinstance(result, list)

    def test_storage_read_file_returns_dict(self, tmp_path: Path) -> None:
        (tmp_path / "hello.md").write_text("# Hello", encoding="utf-8")
        storage = Storage(str(tmp_path))
        result = storage.read_file("hello.md")
        assert isinstance(result, dict)
        assert "text" in result
        assert "source" in result


# --- Logic tests ---


class TestStorageLogic:
    """Logic tests: verify Storage behavior with real file system."""

    def test_storage_read_file_success(self, tmp_path: Path) -> None:
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "auth.md").write_text("# Auth", encoding="utf-8")

        storage = Storage(str(tmp_path))
        result = storage.read_file("docs/auth.md")

        assert result == {"text": "# Auth", "source": "docs/auth.md"}

    def test_storage_read_file_nested_path(self, tmp_path: Path) -> None:
        sub = tmp_path / "sub"
        sub.mkdir()
        deep = sub / "deep"
        deep.mkdir()
        (deep / "file.md").write_text("# Deep", encoding="utf-8")

        storage = Storage(str(tmp_path))
        result = storage.read_file("sub/deep/file.md")

        assert result["source"] == "sub/deep/file.md"
        assert result["text"] == "# Deep"

    def test_storage_path_traversal(self, tmp_path: Path) -> None:
        storage = Storage(str(tmp_path))

        with pytest.raises(ValueError, match="Path traversal"):
            storage.read_file("../../etc/passwd")

    def test_storage_file_not_found(self, tmp_path: Path) -> None:
        storage = Storage(str(tmp_path))

        with pytest.raises(FileNotFoundError, match=r"nonexistent\.md"):
            storage.read_file("nonexistent.md")

    def test_storage_non_md_file(self, tmp_path: Path) -> None:
        (tmp_path / "script.py").write_text('print("hello")', encoding="utf-8")

        storage = Storage(str(tmp_path))

        with pytest.raises(FileNotFoundError):
            storage.read_file("script.py")

    def test_storage_list_files_returns_md_paths(self, tmp_path: Path) -> None:
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "auth.md").write_text("# Auth", encoding="utf-8")
        (tmp_path / "guide.md").write_text("# Guide", encoding="utf-8")
        (tmp_path / "script.py").write_text('print("hello")', encoding="utf-8")

        storage = Storage(str(tmp_path))
        result = storage.list_files()

        assert result == ["docs/auth.md", "guide.md"]

    def test_storage_list_files_empty_directory(self, tmp_path: Path) -> None:
        storage = Storage(str(tmp_path))
        result = storage.list_files()

        assert result == []

    def test_storage_list_files_nested_directories(self, tmp_path: Path) -> None:
        (tmp_path / "a.md").write_text("# A", encoding="utf-8")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "b.md").write_text("# B", encoding="utf-8")
        deep = sub / "deep"
        deep.mkdir()
        (deep / "c.md").write_text("# C", encoding="utf-8")

        storage = Storage(str(tmp_path))
        result = storage.list_files()

        assert result == ["a.md", "sub/b.md", "sub/deep/c.md"]

    def test_storage_empty_file_path(self, tmp_path: Path) -> None:
        storage = Storage(str(tmp_path))

        with pytest.raises(FileNotFoundError):
            storage.read_file("")
