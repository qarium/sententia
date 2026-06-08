from __future__ import annotations

import inspect
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest
import sententia
import sententia.__main__
from sententia.__main__ import main
from sententia.config import SententiaConfig


class TestMainContract:
    """Contract tests for sententia root module and __main__."""

    def test_main_importable(self):
        """main must be importable from sententia.__main__."""
        assert callable(main)

    def test_main_signature(self):
        """main must accept argv: list[str] | None = None and return None."""
        sig = inspect.signature(main)
        params = list(sig.parameters.keys())
        assert params == ["argv"]
        assert sig.parameters["argv"].default is None

    def test_build_parser_removed(self):
        """build_parser has been deleted from __main__."""
        assert not hasattr(sententia.__main__, "build_parser")

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
    """Logic tests for main() with delegated CLI parsing and config."""

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_rest_mode(self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path):
        """main() in REST mode: 3 resources, 0 tools, run with host and port."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        with (
            patch("sententia.api.SearchResource"),
            patch("sententia.api.AskResource"),
            patch("sententia.api.FilesResource"),
        ):
            main(
                [
                    str(tmp_path),
                    "--llm-protocol",
                    "openai",
                    "--llm-url",
                    "http://localhost",
                    "--llm-model",
                    "gpt-4",
                ]
            )

            assert mock_app.add_rest_resource.call_count == 3
            mock_app.add_mcp_tool.assert_not_called()
            mock_app.run.assert_called_once_with(host="0.0.0.0", port=8000)

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_mcp_mode(self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path):
        """main() with --mcp: 3 tools, 0 resources, run called."""
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
            mock_app.add_rest_resource.assert_not_called()
            mock_app.run.assert_called_once()

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_with_env_file(self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path):
        """main() passes --env-file to SententiaConfig."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app
        env_file_path = str(tmp_path / "custom.env")

        with (
            patch("sententia.api.SearchResource"),
            patch("sententia.api.AskResource"),
            patch("sententia.api.FilesResource"),
            patch("sententia.config.SententiaConfig", wraps=SententiaConfig) as spy_config,
        ):
            main(
                [
                    str(tmp_path),
                    "--env-file",
                    env_file_path,
                    "--llm-protocol",
                    "openai",
                    "--llm-url",
                    "http://localhost",
                    "--llm-model",
                    "gpt-4",
                ]
            )

            spy_config.assert_called_once()
            call_kwargs = spy_config.call_args.kwargs
            assert call_kwargs["env_file"] == env_file_path

    def test_main_unknown_protocol_raises_error(self):
        """main() raises ValueError for unknown LLM protocol."""
        from sententia.cli import ParseCliResult  # noqa: PLC0415

        with patch("sententia.cli.parse_cli_args") as mock_parse:
            mock_parse.return_value = ParseCliResult(
                data_dir="data",
                llm_protocol="invalid",
                llm_url="http://api",
                llm_model="test",
            )
            with pytest.raises(ValueError, match="Unknown LLM protocol"):
                main()

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_with_index_path_none(self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path):
        """main() without --index-path passes None to Index (in-memory mode)."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        with (
            patch("sententia.api.SearchResource"),
            patch("sententia.api.AskResource"),
            patch("sententia.api.FilesResource"),
        ):
            main(
                [
                    str(tmp_path),
                    "--llm-protocol",
                    "openai",
                    "--llm-url",
                    "http://localhost",
                    "--llm-model",
                    "gpt-4",
                ]
            )

            call_args = mock_index_cls.call_args
            assert call_args[0][1] is None

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_with_index_path_set(self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path):
        """main() with --index-path passes the path to Index."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        with (
            patch("sententia.api.SearchResource"),
            patch("sententia.api.AskResource"),
            patch("sententia.api.FilesResource"),
        ):
            main(
                [
                    str(tmp_path),
                    "--index-path",
                    "/tmp/test.faiss",
                    "--llm-protocol",
                    "openai",
                    "--llm-url",
                    "http://localhost",
                    "--llm-model",
                    "gpt-4",
                ]
            )

            call_args = mock_index_cls.call_args
            assert call_args[0][1] == "/tmp/test.faiss"

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_with_llm_token_none(self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path):
        """main() without --llm-token passes None to LLM provider."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        with (
            patch("sententia.api.SearchResource"),
            patch("sententia.api.AskResource"),
            patch("sententia.api.FilesResource"),
        ):
            main(
                [
                    str(tmp_path),
                    "--llm-protocol",
                    "openai",
                    "--llm-url",
                    "http://localhost",
                    "--llm-model",
                    "gpt-4",
                ]
            )

            mock_llm_cls.assert_called_once_with("http://localhost", "gpt-4", None)


class TestMainHelpOutput:
    """Tests for CLI help output."""

    def test_help_output(self):
        """python -m sententia --help outputs all arguments."""
        result = subprocess.run(
            [sys.executable, "-m", "sententia", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        expected_args = (
            "--env-file",
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
        # Positional arg shown without -- prefix
        assert "data_dir" in result.stdout
        assert "--data-dir" not in result.stdout


class TestMainProviderTypes:
    """Tests verifying main() uses correct provider types."""

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


class TestMainMcpMode:
    """Logic tests for main() MCP mode."""

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_mcp_flag_creates_tools(
        self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path
    ):
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


class TestMainTopParameter:
    """Tests verifying main() passes top=10 to AskResource/AskTool."""

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_mcp_uses_top_10(
        self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path
    ):
        """main() passes top=10 to AskTool."""
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

            mock_ask_tool.assert_called_once_with(
                mock_index_cls.return_value, mock_llm_cls.return_value, top=10
            )

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_rest_uses_top_10(
        self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path
    ):
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


class TestMainMcpMethodNames:
    """Tests verifying main() uses correct method names."""

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_main_mcp_calls_add_mcp_tool(
        self, mock_storage_cls, mock_index_cls, mock_llm_cls, mock_app_cls, tmp_path
    ):
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
