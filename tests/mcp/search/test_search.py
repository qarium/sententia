from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from sententia.endpoints import MCPTool
from sententia.mcp.search import SearchTool, SearchToolResult


class TestSearchContract:
    def test_search_tool_result_importable(self):
        assert SearchToolResult is not None

    def test_search_tool_importable(self):
        assert SearchTool is not None

    def test_search_tool_is_mcptool_subclass(self):
        assert issubclass(SearchTool, MCPTool)

    def test_search_tool_properties(self):
        mock_index = MagicMock()
        tool = SearchTool(index=mock_index)
        assert tool.name == "search"
        assert tool.description == "Search for relevant documents in the knowledge base"


class TestSearchLogic:
    def test_search_tool_execute_returns_results(self):
        mock_index = MagicMock()
        mock_index.search.return_value = [
            {"text": "auth content", "source": "docs/auth.md", "score": 0.95},
        ]
        tool = SearchTool(index=mock_index)
        results = tool.execute(query="как настроить авторизацию")

        mock_index.search.assert_called_once_with("как настроить авторизацию", 10)
        assert len(results) == 1
        assert isinstance(results[0], SearchToolResult)
        assert results[0].text == "auth content"
        assert results[0].source == "docs/auth.md"
        assert results[0].score == 0.95

    def test_search_tool_execute_empty_results(self):
        mock_index = MagicMock()
        mock_index.search.return_value = []
        tool = SearchTool(index=mock_index)
        results = tool.execute(query="nonexistent")

        assert results == []

    def test_search_tool_default_top(self):
        mock_index = MagicMock()
        mock_index.search.return_value = []
        tool = SearchTool(index=mock_index)
        tool.execute(query="test")

        mock_index.search.assert_called_once_with("test", 10)

    def test_search_tool_execute_custom_top(self):
        mock_index = MagicMock()
        mock_index.search.return_value = []
        tool = SearchTool(index=mock_index)
        tool.execute(query="test", top=3)

        mock_index.search.assert_called_once_with("test", 3)

    def test_search_tool_execute_propagates_error(self):
        mock_index = MagicMock()
        mock_index.search.side_effect = RuntimeError("index corrupted")
        tool = SearchTool(index=mock_index)

        with pytest.raises(RuntimeError, match="index corrupted"):
            tool.execute(query="test")
