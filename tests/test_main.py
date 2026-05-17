from __future__ import annotations

import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest
import sententia
from sententia.__main__ import build_parser, main
from sententia.storage import Storage


class TestMainContract:
    """Contract tests for sententia root module and __main__."""

    def test_main_importable(self):
        """main must be importable from sententia.__main__."""
        assert callable(main)

    def test_storage_importable_from_sententia(self):
        """Storage must be importable from sententia (lazy)."""
        assert hasattr(sententia, "Storage")

    def test_index_importable_from_sententia(self):
        """Index must be importable from sententia (lazy)."""
        assert hasattr(sententia, "Index")

    def test_sententia_app_importable_from_sententia(self):
        """SententiaApp must be importable from sententia (lazy)."""
        assert hasattr(sententia, "SententiaApp")

    def test_llm_providers_importable_from_sententia(self):
        """OpenaiProvider and AnthropicProvider must be importable from sententia (lazy)."""
        assert hasattr(sententia, "OpenaiProvider")
        assert hasattr(sententia, "AnthropicProvider")

    def test_ask_importable_from_sententia(self):
        """ask must be importable from sententia (lazy)."""
        assert hasattr(sententia, "ask")

    def test_openai_provider_importable(self):
        """OpenaiProvider must be importable from sententia.llm."""
        from sententia.llm import OpenaiProvider  # noqa: PLC0415

        assert OpenaiProvider is not None

    def test_anthropic_provider_importable(self):
        """AnthropicProvider must be importable from sententia.llm."""
        from sententia.llm import AnthropicProvider  # noqa: PLC0415

        assert AnthropicProvider is not None

    def test_files_resource_importable(self):
        """FilesResource must be importable from sententia.api."""
        from sententia.api import FilesResource  # noqa: PLC0415

        assert FilesResource is not None

    def test_search_resource_importable(self):
        """SearchResource must be importable from sententia.api."""
        from sententia.api import SearchResource  # noqa: PLC0415

        assert SearchResource is not None

    def test_ask_resource_importable(self):
        """AskResource must be importable from sententia.api."""
        from sententia.api import AskResource  # noqa: PLC0415

        assert AskResource is not None


class TestMainLogic:
    """Logic tests for main() CLI entry point."""

    def test_argparse_parsing_with_defaults(self):
        """main() parses required args and uses defaults for optional ones."""
        args = build_parser().parse_args(
            [
                "/data",
                "--llm-protocol",
                "ollama",
                "--llm-url",
                "http://localhost:11434",
                "--llm-model",
                "llama3",
            ]
        )
        assert args.data_dir == "/data"
        assert args.llm_protocol == "ollama"
        assert args.llm_url == "http://localhost:11434"
        assert args.llm_model == "llama3"
        assert args.index_path is None
        assert args.llm_token is None
        assert args.host == "0.0.0.0"
        assert args.port == 8000
        assert args.mcp is False

    def test_mcp_flag_parsed_true(self):
        """--mcp flag is parsed as True when provided."""
        args = build_parser().parse_args(
            [
                "data",
                "--llm-protocol",
                "openai",
                "--llm-url",
                "http://api",
                "--llm-model",
                "gpt-4",
                "--mcp",
            ]
        )
        assert args.mcp is True

    def test_mcp_flag_default_false(self):
        """--mcp defaults to False when not provided."""
        args = build_parser().parse_args(
            [
                "data",
                "--llm-protocol",
                "openai",
                "--llm-url",
                "http://api",
                "--llm-model",
                "gpt-4",
            ]
        )
        assert args.mcp is False

    def test_argparse_all_args(self):
        """main() parses all arguments including optional ones."""
        args = build_parser().parse_args(
            [
                "/docs",
                "--index-path",
                "/tmp/my.index",
                "--llm-protocol",
                "openai",
                "--llm-url",
                "https://api.openai.com",
                "--llm-model",
                "gpt-4",
                "--llm-token",
                "sk-test",
                "--host",
                "127.0.0.1",
                "--port",
                "9000",
            ]
        )
        assert args.data_dir == "/docs"
        assert args.index_path == "/tmp/my.index"
        assert args.llm_protocol == "openai"
        assert args.llm_url == "https://api.openai.com"
        assert args.llm_model == "gpt-4"
        assert args.llm_token == "sk-test"
        assert args.host == "127.0.0.1"
        assert args.port == 9000

    @patch("uvicorn.run")
    @patch("sententia.index.indexer.SentenceTransformer")
    @patch("sententia.llm.openai.provider.httpx")
    def test_main_creates_all_components(self, mock_httpx, mock_st_cls, mock_run, tmp_path):
        """main() creates all components and starts the server."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
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
        call_kwargs = mock_run.call_args
        assert call_kwargs.kwargs["host"] == "0.0.0.0"
        assert call_kwargs.kwargs["port"] == 8000

    @patch("uvicorn.run")
    @patch("sententia.index.indexer.SentenceTransformer")
    @patch("sententia.llm.openai.provider.httpx")
    def test_main_creates_storage_and_passes_to_files_resource(self, mock_httpx, mock_st_cls, mock_run, tmp_path):
        """main() creates Storage with data_dir and passes it to FilesResource."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
        mock_httpx.post.return_value = mock_response

        with (
            patch("sententia.storage.Storage", wraps=sententia.storage.Storage) as storage_spy,
            patch("sententia.api.FilesResource", wraps=sententia.api.files.FilesResource) as files_res_spy,
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

            storage_spy.assert_called_once()
            call_args = storage_spy.call_args
            assert call_args[0][0] == str(tmp_path)

            files_res_spy.assert_called_once()
            files_call_args = files_res_spy.call_args
            # First positional arg should be a Storage instance
            assert isinstance(files_call_args[0][0], Storage)

    def test_prog_name_is_sententia(self):
        """ArgParser prog should be 'sententia'."""
        parser = build_parser()
        assert parser.prog == "sententia"

    def test_help_output(self):
        """python -m sententia --help outputs all arguments; data-dir is positional, not --data-dir."""
        result = subprocess.run(
            [sys.executable, "-m", "sententia", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        expected_args = (
            "--index-path",
            "--llm-protocol",
            "--llm-url",
            "--llm-model",
            "--llm-token",
            "--host",
            "--port",
            "--mcp",
        )
        for arg in expected_args:
            assert arg in result.stdout
        # Positional arg shown without -- prefix (argparse uses dest name with underscore)
        assert "data_dir" in result.stdout
        assert "--data-dir" not in result.stdout

    def test_positional_arg_after_named_args(self):
        """Positional data_dir can appear after named arguments."""
        args = build_parser().parse_args(
            [
                "--llm-protocol",
                "ollama",
                "--llm-url",
                "http://localhost:11434",
                "--llm-model",
                "llama3",
                "/data",
            ]
        )
        assert args.data_dir == "/data"

    def test_missing_data_dir_exits(self):
        """Missing positional data_dir causes SystemExit."""
        with pytest.raises(SystemExit) as exc_info:
            build_parser().parse_args(
                [
                    "--llm-protocol",
                    "ollama",
                    "--llm-url",
                    "http://localhost:11434",
                    "--llm-model",
                    "llama3",
                ]
            )
        assert exc_info.value.code != 0

    def test_old_data_dir_flag_rejected(self):
        """Using --data-dir as named flag is rejected (it is now positional)."""
        with pytest.raises(SystemExit) as exc_info:
            build_parser().parse_args(
                [
                    "--data-dir",
                    "/data",
                    "--llm-protocol",
                    "ollama",
                    "--llm-url",
                    "http://localhost:11434",
                    "--llm-model",
                    "llama3",
                ]
            )
        assert exc_info.value.code != 0

    @patch("uvicorn.run")
    @patch("sententia.index.indexer.SentenceTransformer")
    @patch("sententia.llm.openai.provider.httpx")
    def test_main_passes_storage_to_index(self, mock_httpx, mock_st_cls, mock_run, tmp_path):
        """main() creates Storage and passes it to Index constructor."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
        mock_httpx.post.return_value = mock_response

        with patch("sententia.index.Index") as mock_index_cls:
            mock_index_cls.return_value.search.return_value = []
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

            call_args = mock_index_cls.call_args
            assert isinstance(call_args[0][0], Storage)

    @patch("uvicorn.run")
    @patch("sententia.index.indexer.SentenceTransformer")
    @patch("sententia.llm.openai.provider.httpx")
    def test_main_without_index_path_creates_in_memory_index(self, mock_httpx, mock_st_cls, mock_run, tmp_path):
        """main() without --index-path passes None to Index (in-memory mode)."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
        mock_httpx.post.return_value = mock_response

        with patch("sententia.index.Index") as mock_index_cls:
            mock_index_cls.return_value.search.return_value = []
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

            call_args = mock_index_cls.call_args
            assert call_args[0][1] is None

    @patch("uvicorn.run")
    @patch("sententia.index.indexer.SentenceTransformer")
    @patch("sententia.llm.openai.provider.httpx")
    def test_main_with_index_path_creates_persistent_index(self, mock_httpx, mock_st_cls, mock_run, tmp_path):
        """main() with --index-path passes the path string to Index."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
        mock_httpx.post.return_value = mock_response
        index_file = tmp_path / "test.faiss"

        with patch("sententia.index.Index") as mock_index_cls:
            mock_index_cls.return_value.search.return_value = []
            main(
                [
                    str(tmp_path),
                    "--index-path",
                    str(index_file),
                    "--llm-protocol",
                    "ollama",
                    "--llm-url",
                    "http://localhost:11434",
                    "--llm-model",
                    "llama3",
                ]
            )

            call_args = mock_index_cls.call_args
            assert call_args[0][1] == str(index_file)


class TestMainMcpMode:
    """Logic tests for main() MCP mode."""

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_mcp_flag_creates_tools(self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path):
        """main() with --mcp creates SearchTool, AskTool, FilesTool and calls add_mcp_tool 3 times."""
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
                    "ollama",
                    "--llm-url",
                    "http://localhost:11434",
                    "--llm-model",
                    "llama3",
                    "--mcp",
                ]
            )

            mock_search_tool.assert_called_once()
            mock_ask_tool.assert_called_once()
            mock_files_tool.assert_called_once()
            assert mock_app.add_mcp_tool.call_count == 3
            mock_app.run.assert_called_once()

    @patch("uvicorn.run")
    @patch("sententia.index.indexer.SentenceTransformer")
    @patch("sententia.llm.openai.provider.httpx")
    def test_main_without_mcp_uses_endpoints(self, mock_httpx, mock_st_cls, mock_run, tmp_path):
        """main() without --mcp runs REST mode (regression test)."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
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
        call_kwargs = mock_run.call_args
        assert call_kwargs.kwargs["host"] == "0.0.0.0"
        assert call_kwargs.kwargs["port"] == 8000

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_mcp_does_not_create_rest_resources(
        self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path
    ):
        """main() with --mcp does not create REST resources."""
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
                    "ollama",
                    "--llm-url",
                    "http://localhost:11434",
                    "--llm-model",
                    "llama3",
                    "--mcp",
                ]
            )

            mock_search_res.assert_not_called()
            mock_ask_res.assert_not_called()
            mock_files_res.assert_not_called()
            mock_app.add_rest_resource.assert_not_called()


class TestMainNewProviderTypes:
    """Contract tests verifying main() uses new provider types."""

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_uses_openai_provider_for_ollama(
        self, mock_storage_cls, mock_index_cls, mock_openai_cls, mock_app_cls, tmp_path
    ):
        """main() with --llm-protocol ollama creates OpenaiProvider."""
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
                ]
            )

            mock_openai_cls.assert_called_once_with("http://localhost:11434", "llama3", None)

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_uses_openai_provider_for_openai(
        self, mock_storage_cls, mock_index_cls, mock_openai_cls, mock_app_cls, tmp_path
    ):
        """main() with --llm-protocol openai creates OpenaiProvider."""
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
                    "openai",
                    "--llm-url",
                    "http://api",
                    "--llm-model",
                    "gpt-4",
                    "--llm-token",
                    "sk-test",
                    "--mcp",
                ]
            )

            mock_openai_cls.assert_called_once_with("http://api", "gpt-4", "sk-test")

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.AnthropicProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_uses_anthropic_provider_for_anthropic(
        self, mock_storage_cls, mock_index_cls, mock_anthropic_cls, mock_app_cls, tmp_path
    ):
        """main() with --llm-protocol anthropic creates AnthropicProvider."""
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
                    "anthropic",
                    "--llm-url",
                    "https://api.anthropic.com",
                    "--llm-model",
                    "claude-3",
                    "--llm-token",
                    "sk-ant-test",
                    "--mcp",
                ]
            )

            mock_anthropic_cls.assert_called_once_with("https://api.anthropic.com", "claude-3", "sk-ant-test")

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_mcp_uses_top_10(self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path):
        """main() passes top=10 to AskTool (not top=5)."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        with (
            patch("sententia.mcp.SearchTool"),
            patch("sententia.mcp.AskTool") as mock_ask_tool,
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
                ]
            )

            mock_ask_tool.assert_called_once_with(mock_index_cls.return_value, mock_llm_cls.return_value, top=10)

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_rest_uses_top_10(self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path):
        """main() in REST mode passes top=10 to AskResource."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        with (
            patch("sententia.api.SearchResource"),
            patch("sententia.api.AskResource") as mock_ask_resource,
            patch("sententia.api.FilesResource"),
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

            mock_ask_resource.assert_called_once()
            call_kwargs = mock_ask_resource.call_args
            assert call_kwargs.kwargs.get("top", call_kwargs[1].get("top")) == 10

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_mcp_calls_add_mcp_tool(self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path):
        """main() calls add_mcp_tool (not add_tool)."""
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
                ]
            )

            assert mock_app.add_mcp_tool.call_count == 3
            mock_app.add_tool.assert_not_called()


class TestMainEnvVarFallback:
    """Test env var fallback for --llm-token."""

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_token_fallback_to_env_var(
        self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path
    ):
        """main() falls back to SENTENTIA_LLM_TOKEN env var when --llm-token is not provided."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        with (
            patch("sententia.mcp.SearchTool"),
            patch("sententia.mcp.AskTool"),
            patch("sententia.mcp.FilesTool"),
            patch.dict("os.environ", {"SENTENTIA_LLM_TOKEN": "env-token"}),
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

            mock_llm_cls.assert_called_once_with("http://api", "gpt-4", "env-token")
