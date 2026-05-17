from __future__ import annotations

from unittest.mock import MagicMock, patch

from sententia.__main__ import main


class TestMainMcpEndToEnd:
    """End-to-end integration: main() with --mcp exercises the full MCP flow."""

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_mcp_full_flow_creates_components_and_tools(
        self, mock_storage_cls, mock_index_cls, mock_openai_cls, mock_app_cls, tmp_path
    ):
        """main() --mcp: Storage->Index->OpenaiProvider->SearchTool->AskTool->FilesTool->add_mcp_tool x3->run."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        with (
            patch("sententia.mcp.SearchTool") as mock_search_tool,
            patch("sententia.mcp.AskTool") as mock_ask_tool,
            patch("sententia.mcp.FilesTool") as mock_files_tool,
        ):
            main(
                [
                    str(tmp_path),
                    "--llm-protocol",
                    "openai",
                    "--llm-url",
                    "http://api",
                    "--llm-model",
                    "gpt-4",
                    "--mcp",
                ]
            )

            # Domain components created
            mock_storage_cls.assert_called_once_with(str(tmp_path))
            mock_index_cls.assert_called_once_with(mock_storage_cls.return_value, None)
            mock_openai_cls.assert_called_once_with("http://api", "gpt-4", None)

            # MCP tools created with correct dependencies
            mock_search_tool.assert_called_once_with(mock_index_cls.return_value)
            mock_ask_tool.assert_called_once_with(mock_index_cls.return_value, mock_openai_cls.return_value, top=10)
            mock_files_tool.assert_called_once_with(mock_storage_cls.return_value)

            # Tools registered with app
            assert mock_app.add_mcp_tool.call_count == 3
            mock_app.add_mcp_tool.assert_any_call(mock_search_tool.return_value)
            mock_app.add_mcp_tool.assert_any_call(mock_ask_tool.return_value)
            mock_app.add_mcp_tool.assert_any_call(mock_files_tool.return_value)

            # App run called
            mock_app.run.assert_called_once_with(host="0.0.0.0", port=8000)

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_mcp_custom_host_port(self, mock_storage_cls, mock_index_cls, mock_openai_cls, mock_app_cls, tmp_path):
        """main() --mcp passes custom host/port to app.run()."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        with (
            patch("sententia.mcp.SearchTool"),
            patch("sententia.mcp.AskTool"),
            patch("sententia.mcp.FilesTool"),
        ):
            main(
                [
                    str(tmp_path),
                    "--llm-protocol",
                    "ollama",
                    "--llm-url",
                    "http://localhost:11434",
                    "--llm-model",
                    "llama3",
                    "--mcp",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "9000",
                ]
            )

            mock_app.run.assert_called_once_with(host="127.0.0.1", port=9000)


class TestMainRestEndToEnd:
    """End-to-end integration: main() without --mcp exercises REST flow."""

    @patch("uvicorn.run")
    @patch("sententia.index.indexer.SentenceTransformer")
    @patch("sententia.llm.openai.provider.httpx")
    def test_rest_mode_creates_resources(self, mock_httpx, mock_st_cls, mock_run, tmp_path):
        """main() without --mcp creates REST resources and starts uvicorn."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_httpx.post.return_value = mock_response

        main(
            [
                str(tmp_path),
                "--llm-protocol",
                "ollama",
                "--llm-url",
                "http://localhost:11434",
                "--llm-model",
                "llama3",
            ]
        )

        mock_run.assert_called_once()
        assert mock_run.call_args.kwargs["host"] == "0.0.0.0"
        assert mock_run.call_args.kwargs["port"] == 8000


class TestMainModeExclusivity:
    """Verify MCP and REST modes are mutually exclusive."""

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_mcp_mode_does_not_create_rest_resources(
        self, mock_storage_cls, mock_index_cls, mock_openai_cls, mock_app_cls, tmp_path
    ):
        """main() with --mcp does not instantiate SearchResource, AskResource, FilesResource."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        with (
            patch("sententia.mcp.SearchTool"),
            patch("sententia.mcp.AskTool"),
            patch("sententia.mcp.FilesTool"),
            patch("sententia.api.SearchResource") as mock_search_res,
            patch("sententia.api.AskResource") as mock_ask_res,
            patch("sententia.api.FilesResource") as mock_files_res,
        ):
            main(
                [
                    str(tmp_path),
                    "--llm-protocol",
                    "openai",
                    "--llm-url",
                    "http://api",
                    "--llm-model",
                    "gpt-4",
                    "--mcp",
                ]
            )

            mock_search_res.assert_not_called()
            mock_ask_res.assert_not_called()
            mock_files_res.assert_not_called()
            mock_app.add_rest_resource.assert_not_called()

    @patch("uvicorn.run")
    @patch("sententia.index.indexer.SentenceTransformer")
    @patch("sententia.llm.openai.provider.httpx")
    def test_rest_mode_does_not_create_mcp_tools(self, mock_httpx, mock_st_cls, mock_run, tmp_path):
        """main() without --mcp does not import or create MCP tools."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_httpx.post.return_value = mock_response

        with (
            patch("sententia.mcp.SearchTool") as mock_search,
            patch("sententia.mcp.AskTool") as mock_ask,
            patch("sententia.mcp.FilesTool") as mock_files,
        ):
            main(
                [
                    str(tmp_path),
                    "--llm-protocol",
                    "ollama",
                    "--llm-url",
                    "http://localhost:11434",
                    "--llm-model",
                    "llama3",
                ]
            )

            mock_search.assert_not_called()
            mock_ask.assert_not_called()
            mock_files.assert_not_called()
