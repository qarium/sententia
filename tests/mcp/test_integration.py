from __future__ import annotations

from unittest.mock import MagicMock, patch

from sententia.app.app import SententiaApp, _create_wrapper
from sententia.mcp import AskTool, FilesTool, SearchTool


class TestFullMcpRegistrationFlow:
    """Integration: registering all three tools with SententiaApp."""

    def test_register_all_tools_creates_mcp_instance(self):
        mock_index = MagicMock()
        mock_llm = MagicMock()
        mock_storage = MagicMock()

        search = SearchTool(mock_index)
        ask = AskTool(mock_index, mock_llm, top=5)
        files = FilesTool(mock_storage)

        app = SententiaApp()
        app.add_mcp_tool(search)
        app.add_mcp_tool(ask)
        app.add_mcp_tool(files)

        assert app._mcp is not None
        assert len(app._tools) == 3

    def test_register_all_tools_preserves_order(self):
        mock_index = MagicMock()
        mock_llm = MagicMock()
        mock_storage = MagicMock()

        search = SearchTool(mock_index)
        ask = AskTool(mock_index, mock_llm)
        files = FilesTool(mock_storage)

        app = SententiaApp()
        app.add_mcp_tool(search)
        app.add_mcp_tool(ask)
        app.add_mcp_tool(files)

        assert isinstance(app._tools[0], SearchTool)
        assert isinstance(app._tools[1], AskTool)
        assert isinstance(app._tools[2], FilesTool)

    def test_mcp_mode_run_with_all_tools(self):
        mock_index = MagicMock()
        mock_llm = MagicMock()
        mock_storage = MagicMock()

        app = SententiaApp()
        app.add_mcp_tool(SearchTool(mock_index))
        app.add_mcp_tool(AskTool(mock_index, mock_llm))
        app.add_mcp_tool(FilesTool(mock_storage))

        app._mcp.run = MagicMock()
        app._mcp.settings = MagicMock()

        app.run(host="0.0.0.0", port=8080)

        assert app._mcp.settings.host == "0.0.0.0"
        assert app._mcp.settings.port == 8080
        app._mcp.run.assert_called_once_with(transport="streamable-http")


class TestWrapperDelegation:
    """Integration: wrapper functions delegate to tool.execute() correctly."""

    def test_search_tool_wrapper_delegates(self):
        mock_index = MagicMock()
        mock_index.search.return_value = [{"text": "result", "source": "doc.md", "score": 0.9}]
        tool = SearchTool(mock_index)

        wrapper = _create_wrapper(tool)
        result = wrapper(query="test query")

        mock_index.search.assert_called_once_with("test query", 10)
        assert len(result) == 1
        assert result[0].source == "doc.md"

    def test_ask_tool_wrapper_delegates(self):
        mock_index = MagicMock()
        mock_llm = MagicMock()
        expected = {"answer": "Yes", "sources": ["doc.md"]}

        with patch("sententia.mcp.ask.ask.rag.ask", return_value=expected):
            tool = AskTool(mock_index, mock_llm, top=3)
            wrapper = _create_wrapper(tool)
            result = wrapper(query="Is this working?")

        assert result.answer == "Yes"
        assert "doc.md" in result.sources

    def test_files_tool_wrapper_delegates(self):
        mock_storage = MagicMock()
        mock_storage.read_file.return_value = {
            "text": "# Title",
            "source": "docs/title.md",
        }
        tool = FilesTool(mock_storage)

        wrapper = _create_wrapper(tool)
        result = wrapper(path="docs/title.md")

        mock_storage.read_file.assert_called_once_with("docs/title.md")
        assert result.text == "# Title"

    def test_search_tool_wrapper_custom_top(self):
        mock_index = MagicMock()
        mock_index.search.return_value = []
        tool = SearchTool(mock_index)

        wrapper = _create_wrapper(tool)
        wrapper(query="test", top=2)

        mock_index.search.assert_called_once_with("test", 2)


class TestWrapperMetadata:
    """Integration: wrapper functions carry correct name, doc, and signature."""

    def test_search_wrapper_name_and_doc(self):
        mock_index = MagicMock()
        tool = SearchTool(mock_index)
        wrapper = _create_wrapper(tool)

        assert wrapper.__name__ == "search"
        assert wrapper.__doc__ == "Search for relevant documents in the knowledge base"

    def test_ask_wrapper_name_and_doc(self):
        mock_index = MagicMock()
        mock_llm = MagicMock()
        tool = AskTool(mock_index, mock_llm)
        wrapper = _create_wrapper(tool)

        assert wrapper.__name__ == "ask"
        assert wrapper.__doc__ == "Ask a question and get an answer based on indexed documents"

    def test_files_wrapper_name_and_doc(self):
        mock_storage = MagicMock()
        tool = FilesTool(mock_storage)
        wrapper = _create_wrapper(tool)

        assert wrapper.__name__ == "files"
        assert wrapper.__doc__ == "Read file content by path"

    def test_wrapper_signature_excludes_self(self):
        mock_index = MagicMock()
        tool = SearchTool(mock_index)
        wrapper = _create_wrapper(tool)

        params = list(wrapper.__signature__.parameters.keys())
        assert "self" not in params
        assert "query" in params
        assert "top" in params

    def test_wrapper_signature_preserves_types(self):
        mock_index = MagicMock()
        mock_llm = MagicMock()
        tool = AskTool(mock_index, mock_llm)
        wrapper = _create_wrapper(tool)

        params = wrapper.__signature__.parameters
        assert "query" in params
        assert "self" not in params
