from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from sententia.endpoints import MCPTool
from sententia.llm.provider.errors import LLMProviderError
from sententia.mcp.ask import AskTool, AskToolResult


class TestAskContract:
    def test_ask_tool_result_importable(self):
        assert AskToolResult is not None

    def test_ask_tool_importable(self):
        assert AskTool is not None

    def test_ask_tool_is_mcptool_subclass(self):
        assert issubclass(AskTool, MCPTool)

    def test_ask_tool_properties(self):
        mock_index = MagicMock()
        mock_llm = MagicMock()
        tool = AskTool(index=mock_index, llm_provider=mock_llm)
        assert tool.name == "ask"
        assert tool.description == "Ask a question and get an answer based on indexed documents"


class TestAskLogic:
    def test_ask_tool_execute_returns_result(self):
        mock_index = MagicMock()
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Настройте OAuth2"
        mock_index.search.return_value = [
            {"text": "auth guide", "source": "auth.md", "score": 0.9},
        ]
        tool = AskTool(index=mock_index, llm_provider=mock_llm)
        result = tool.execute(query="как настроить авторизацию")

        assert isinstance(result, AskToolResult)
        assert result.answer == "Настройте OAuth2"
        assert result.sources == ["auth.md"]

    def test_ask_tool_execute_llm_error(self):
        mock_index = MagicMock()
        mock_llm = MagicMock()
        mock_llm.generate.side_effect = LLMProviderError("API error")
        mock_index.search.return_value = [
            {"text": "auth guide", "source": "auth.md", "score": 0.9},
        ]
        tool = AskTool(index=mock_index, llm_provider=mock_llm)

        with pytest.raises(LLMProviderError, match="API error"):
            tool.execute(query="test")

    def test_ask_tool_default_top(self):
        mock_index = MagicMock()
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "answer"
        mock_index.search.return_value = []
        tool = AskTool(index=mock_index, llm_provider=mock_llm)
        tool.execute(query="test")

        mock_index.search.assert_called_once_with("test", 10)

    def test_ask_tool_execute_custom_top(self):
        mock_index = MagicMock()
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "answer"
        mock_index.search.return_value = []
        tool = AskTool(index=mock_index, llm_provider=mock_llm, top=3)
        tool.execute(query="test")

        mock_index.search.assert_called_once_with("test", 3)
