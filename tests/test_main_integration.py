"""End-to-end integration tests for cli + config + main pipeline.

Verifies the full path: parse_cli_args -> SententiaConfig -> Storage -> Index ->
LLM Provider -> Resources/Tools -> SententiaApp.run.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

from sententia.__main__ import main
from sententia.config import SententiaConfig


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


class TestCliToConfigPipeline:
    """Integration: parse_cli_args -> cli_overrides -> SententiaConfig."""

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_rest_full_pipeline_cli_overrides_passed_to_config(
        self, mock_storage_cls, mock_index_cls, mock_openai_cls, mock_app_cls, tmp_path
    ):
        """REST: parse_cli_args produces values that flow as cli_overrides into SententiaConfig."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        with (
            patch("sententia.api.SearchResource"),
            patch("sententia.api.AskResource"),
            patch("sententia.api.FilesResource"),
            patch("sententia.config.SententiaConfig", wraps=SententiaConfig) as spy_config,
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

            spy_config.assert_called_once()
            call_kwargs = spy_config.call_args.kwargs

            # cli_overrides contain only explicitly provided CLI values (non-None)
            overrides = call_kwargs["cli_overrides"]
            assert overrides["data_dir"] == str(tmp_path)
            assert "index_path" not in overrides
            assert overrides["llm_protocol"] == "openai"
            assert overrides["llm_url"] == "http://localhost"
            assert overrides["llm_model"] == "gpt-4"
            assert "llm_token" not in overrides
            assert "mcp" not in overrides
            assert "host" not in overrides
            assert "port" not in overrides

            # Verify components created with config values
            mock_storage_cls.assert_called_once_with(str(tmp_path))
            mock_index_cls.assert_called_once_with(mock_storage_cls.return_value, None)
            mock_openai_cls.assert_called_once_with("http://localhost", "gpt-4", None)

            assert mock_app.add_rest_resource.call_count == 3
            mock_app.run.assert_called_once_with(host="0.0.0.0", port=8000)

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_mcp_full_pipeline_cli_overrides_passed_to_config(
        self, mock_storage_cls, mock_index_cls, mock_openai_cls, mock_app_cls, tmp_path
    ):
        """MCP: parse_cli_args produces values that flow as cli_overrides into SententiaConfig."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        with (
            patch("sententia.mcp.SearchTool"),
            patch("sententia.mcp.AskTool"),
            patch("sententia.mcp.FilesTool"),
            patch("sententia.config.SententiaConfig", wraps=SententiaConfig) as spy_config,
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
                    "192.168.1.1",
                    "--port",
                    "9999",
                    "--llm-token",
                    "sk-test",
                ]
            )

            spy_config.assert_called_once()
            call_kwargs = spy_config.call_args.kwargs

            overrides = call_kwargs["cli_overrides"]
            assert overrides["data_dir"] == str(tmp_path)
            assert overrides["llm_protocol"] == "ollama"
            assert overrides["llm_url"] == "http://localhost:11434"
            assert overrides["llm_model"] == "llama3"
            assert overrides["mcp"] is True
            assert overrides["host"] == "192.168.1.1"
            assert overrides["port"] == 9999
            assert overrides["llm_token"] == "sk-test"

            # Verify components use config values (not raw args)
            mock_openai_cls.assert_called_once_with("http://localhost:11434", "llama3", "sk-test")
            assert mock_app.add_mcp_tool.call_count == 3
            mock_app.run.assert_called_once_with(host="192.168.1.1", port=9999)


class TestEnvFilePropagation:
    """Integration: --env-file propagates through parse_cli_args -> SententiaConfig."""

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_env_file_passed_through_stack(
        self, mock_storage_cls, mock_index_cls, mock_openai_cls, mock_app_cls, tmp_path
    ):
        """--env-file from CLI reaches SententiaConfig(env_file=...)."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        env_file_path = tmp_path / "custom.env"

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
                    str(env_file_path),
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
            assert call_kwargs["env_file"] == str(env_file_path)

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_env_file_values_accessible_when_cli_does_not_override(  # noqa: PLR0913
        self, mock_storage_cls, mock_index_cls, mock_openai_cls, mock_app_cls, tmp_path, monkeypatch
    ):
        """Env-file provides llm_token when --llm-token is not passed via CLI."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        # Clean ENV so only env-file provides the token
        for key in list(os.environ):
            if key.startswith("SENTENTIA_"):
                monkeypatch.delenv(key, raising=False)

        env_file = tmp_path / "test.env"
        env_file.write_text("SENTENTIA_LLM_TOKEN=sk-from-file\n")

        with (
            patch("sententia.api.SearchResource"),
            patch("sententia.api.AskResource"),
            patch("sententia.api.FilesResource"),
        ):
            main(
                [
                    str(tmp_path),
                    "--env-file",
                    str(env_file),
                    "--llm-protocol",
                    "openai",
                    "--llm-url",
                    "http://localhost",
                    "--llm-model",
                    "gpt-4",
                ]
            )

            # Token comes from env-file, not CLI
            mock_openai_cls.assert_called_once_with("http://localhost", "gpt-4", "sk-from-file")


class TestConfigPriorityIntegration:
    """Integration: ENV + cli_overrides produce correct results through main()."""

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_cli_overrides_override_env_vars(  # noqa: PLR0913
        self, mock_storage_cls, mock_index_cls, mock_openai_cls, mock_app_cls, tmp_path, monkeypatch
    ):
        """Explicit CLI values take priority over ENV variables."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        # Set ENV vars that should be overridden by explicit CLI args
        monkeypatch.setenv("SENTENTIA_LLM_PROTOCOL", "anthropic")
        monkeypatch.setenv("SENTENTIA_HOST", "10.0.0.1")
        monkeypatch.setenv("SENTENTIA_PORT", "9000")

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
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "5000",
                ]
            )

            # Explicit CLI values win over ENV
            mock_openai_cls.assert_called_once_with("http://localhost", "gpt-4", None)
            mock_app.run.assert_called_once_with(host="127.0.0.1", port=5000)

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_env_port_used_when_no_explicit_cli_port(  # noqa: PLR0913
        self, mock_storage_cls, mock_index_cls, mock_openai_cls, mock_app_cls, tmp_path, monkeypatch
    ):
        """ENV port takes effect when --port is not explicitly passed on CLI."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        # Clean ENV
        for key in list(os.environ):
            if key.startswith("SENTENTIA_"):
                monkeypatch.delenv(key, raising=False)

        # ENV sets port to 7000
        monkeypatch.setenv("SENTENTIA_PORT", "7000")

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

            # ENV port (7000) takes effect since --port was not explicitly passed
            mock_app.run.assert_called_once_with(host="0.0.0.0", port=7000)

    @patch("sententia.app.SententiaApp")
    @patch("sententia.llm.OpenaiProvider")
    @patch("sententia.index.Index")
    @patch("sententia.storage.Storage")
    def test_env_file_plus_cli_overrides_priority_chain(  # noqa: PLR0913
        self, mock_storage_cls, mock_index_cls, mock_openai_cls, mock_app_cls, tmp_path, monkeypatch
    ):
        """Full priority: cli_overrides > ENV > env-file > defaults through main()."""
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        # Clean all SENTENTIA_ vars
        for key in list(os.environ):
            if key.startswith("SENTENTIA_"):
                monkeypatch.delenv(key, raising=False)

        # ENV sets host
        monkeypatch.setenv("SENTENTIA_HOST", "10.0.0.1")

        # env-file also sets host and token
        env_file = tmp_path / "prio.env"
        env_file.write_text("SENTENTIA_HOST=10.0.0.2\nSENTENTIA_LLM_TOKEN=sk-from-file\n")

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
                    str(env_file),
                    "--llm-protocol",
                    "openai",
                    "--llm-url",
                    "http://localhost",
                    "--llm-model",
                    "gpt-4",
                    "--host",
                    "127.0.0.1",
                    "--llm-token",
                    "sk-explicit-cli",
                ]
            )

            # Verify SententiaConfig was called with cli_overrides
            spy_config.assert_called_once()
            call_kwargs = spy_config.call_args.kwargs
            assert call_kwargs["env_file"] == str(env_file)

            overrides = call_kwargs["cli_overrides"]
            # Explicit CLI host wins over ENV (10.0.0.1) and env-file (10.0.0.2)
            assert overrides["host"] == "127.0.0.1"
            # Explicit CLI token wins over env-file
            assert overrides["llm_token"] == "sk-explicit-cli"

            # App uses config values derived from CLI overrides
            mock_app.run.assert_called_once_with(host="127.0.0.1", port=8000)
            mock_openai_cls.assert_called_once_with("http://localhost", "gpt-4", "sk-explicit-cli")
