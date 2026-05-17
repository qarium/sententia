from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from sententia.endpoints import MCPTool
from sententia.mcp.files import FilesTool, FilesToolResult


class TestFilesContract:
    def test_files_tool_result_importable(self):
        assert FilesToolResult is not None

    def test_files_tool_importable(self):
        assert FilesTool is not None

    def test_files_tool_is_mcptool_subclass(self):
        assert issubclass(FilesTool, MCPTool)

    def test_files_tool_properties(self):
        mock_storage = MagicMock()
        tool = FilesTool(storage=mock_storage)
        assert tool.name == "files"
        assert tool.description == "Read file content by path"


class TestFilesLogic:
    def test_files_tool_execute_returns_result(self):
        mock_storage = MagicMock()
        mock_storage.read_file.return_value = {
            "text": "# Auth Guide",
            "source": "docs/auth.md",
        }
        tool = FilesTool(storage=mock_storage)
        result = tool.execute(path="docs/auth.md")

        mock_storage.read_file.assert_called_once_with("docs/auth.md")
        assert isinstance(result, FilesToolResult)
        assert result.text == "# Auth Guide"
        assert result.source == "docs/auth.md"

    def test_files_tool_execute_not_found(self):
        mock_storage = MagicMock()
        mock_storage.read_file.side_effect = FileNotFoundError("not found")
        tool = FilesTool(storage=mock_storage)

        with pytest.raises(FileNotFoundError):
            tool.execute(path="missing.md")

    def test_files_tool_execute_permission_error(self):
        mock_storage = MagicMock()
        mock_storage.read_file.side_effect = PermissionError("denied")
        tool = FilesTool(storage=mock_storage)

        with pytest.raises(PermissionError):
            tool.execute(path="/etc/shadow")

    def test_files_tool_execute_path_traversal(self):
        mock_storage = MagicMock()
        mock_storage.read_file.side_effect = ValueError("path traversal detected")
        tool = FilesTool(storage=mock_storage)

        with pytest.raises(FileNotFoundError):
            tool.execute(path="../../../etc/passwd")
