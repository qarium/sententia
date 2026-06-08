from __future__ import annotations

import inspect
from unittest.mock import patch

import pytest
from sententia.cli import ParseCliResult, parse_cli_args


class TestCliContract:
    """Contract tests for sententia.cli module."""

    def test_parse_cli_result_importable(self):
        """ParseCliResult must be importable from sententia.cli."""
        assert ParseCliResult is not None

    def test_parse_cli_args_importable(self):
        """parse_cli_args must be importable from sententia.cli."""
        assert callable(parse_cli_args)

    def test_parse_cli_args_signature(self):
        """parse_cli_args must accept argv: list[str] | None = None."""
        sig = inspect.signature(parse_cli_args)
        params = sig.parameters
        assert "argv" in params
        assert params["argv"].default is None

    def test_parse_cli_result_has_10_properties(self):
        """ParseCliResult must have 10 properties with correct types."""
        annotations = ParseCliResult.model_fields
        expected = {
            "data_dir": "str",
            "env_file": "str",
            "index_path": "str",
            "llm_protocol": "str",
            "llm_url": "str",
            "llm_model": "str",
            "llm_token": "str",
            "mcp": "bool",
            "host": "str",
            "port": "int",
        }
        assert set(annotations.keys()) == set(expected.keys()), (
            f"Properties mismatch: {set(annotations.keys())} vs {set(expected.keys())}"
        )


class TestParseCliArgsPositive:
    """Positive logic tests for parse_cli_args."""

    def test_parse_cli_args_minimal_required_args(self):
        """Minimal required args produce correct defaults for optional fields."""
        result = parse_cli_args(
            [
                "data_dir",
                "--llm-protocol",
                "openai",
                "--llm-url",
                "http://localhost:11434",
                "--llm-model",
                "gpt-4",
            ]
        )

        assert result.data_dir == "data_dir"
        assert result.env_file is None
        assert result.index_path is None
        assert result.llm_protocol == "openai"
        assert result.llm_url == "http://localhost:11434"
        assert result.llm_model == "gpt-4"
        assert result.llm_token is None
        assert result.mcp is None
        assert result.host is None
        assert result.port is None

    def test_parse_cli_args_all_options(self):
        """All options including env-file, mcp, port produce correct values."""
        result = parse_cli_args(
            [
                "/docs",
                "--env-file",
                ".env.prod",
                "--index-path",
                "/tmp/index.faiss",
                "--llm-protocol",
                "anthropic",
                "--llm-url",
                "https://api.anthropic.com",
                "--llm-model",
                "claude-3",
                "--llm-token",
                "sk-test",
                "--mcp",
                "--host",
                "127.0.0.1",
                "--port",
                "9000",
            ]
        )

        assert result.data_dir == "/docs"
        assert result.env_file == ".env.prod"
        assert result.index_path == "/tmp/index.faiss"
        assert result.llm_protocol == "anthropic"
        assert result.llm_url == "https://api.anthropic.com"
        assert result.llm_model == "claude-3"
        assert result.llm_token == "sk-test"
        assert result.mcp is True
        assert result.host == "127.0.0.1"
        assert result.port == 9000

    def test_parse_cli_args_returns_parse_cli_result_type(self):
        """parse_cli_args returns a ParseCliResult instance."""
        result = parse_cli_args(
            [
                "data",
                "--llm-protocol",
                "ollama",
                "--llm-url",
                "http://localhost:11434",
                "--llm-model",
                "llama3",
            ]
        )

        assert isinstance(result, ParseCliResult)


class TestParseCliArgsNegative:
    """Negative logic tests for parse_cli_args."""

    def test_parse_cli_args_missing_data_dir(self):
        """Missing positional data_dir causes SystemExit."""
        with pytest.raises(SystemExit):
            parse_cli_args(
                [
                    "--llm-protocol",
                    "openai",
                    "--llm-url",
                    "http://localhost:11434",
                    "--llm-model",
                    "gpt-4",
                ]
            )

    def test_parse_cli_args_missing_required_protocol(self):
        """Missing --llm-protocol causes SystemExit."""
        with pytest.raises(SystemExit):
            parse_cli_args(
                [
                    "data",
                    "--llm-url",
                    "http://localhost:11434",
                    "--llm-model",
                    "gpt-4",
                ]
            )

    def test_parse_cli_args_invalid_protocol(self):
        """Invalid --llm-protocol value causes SystemExit."""
        with pytest.raises(SystemExit):
            parse_cli_args(
                [
                    "data",
                    "--llm-protocol",
                    "invalid",
                    "--llm-url",
                    "http://localhost:11434",
                    "--llm-model",
                    "gpt-4",
                ]
            )


class TestParseCliArgsEdge:
    """Edge case logic tests for parse_cli_args."""

    def test_parse_cli_args_none_argv(self):
        """parse_cli_args(None) uses sys.argv[1:]."""
        with patch(
            "sys.argv",
            ["sententia", "data", "--llm-protocol", "ollama", "--llm-url", "http://api", "--llm-model", "llama3"],
        ):
            result = parse_cli_args(None)

        assert isinstance(result, ParseCliResult)
        assert result.data_dir == "data"
        assert result.llm_protocol == "ollama"

    def test_parse_cli_args_missing_required_url(self):
        """Missing --llm-url causes SystemExit."""
        with pytest.raises(SystemExit):
            parse_cli_args(
                [
                    "data",
                    "--llm-protocol",
                    "openai",
                    "--llm-model",
                    "gpt-4",
                ]
            )

    def test_parse_cli_args_missing_required_model(self):
        """Missing --llm-model causes SystemExit."""
        with pytest.raises(SystemExit):
            parse_cli_args(
                [
                    "data",
                    "--llm-protocol",
                    "openai",
                    "--llm-url",
                    "http://api",
                ]
            )
