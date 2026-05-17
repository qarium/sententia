from __future__ import annotations

import inspect

from sententia.index import Index


class TestIndexContract:
    """Contract tests: verify Index is importable and has correct interface."""

    def test_index_importable(self) -> None:
        assert Index is not None

    def test_index_constructor(self) -> None:
        sig = inspect.signature(Index.__init__)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "storage" in params
        assert "index_path" in params
        assert "default_top" in params
        assert sig.parameters["index_path"].default is None
        assert sig.parameters["default_top"].default == 10

    def test_index_has_methods(self) -> None:
        assert hasattr(Index, "index_directory")
        assert hasattr(Index, "search")
        assert hasattr(Index, "save")
        assert hasattr(Index, "load")
