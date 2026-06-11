from __future__ import annotations

import inspect
import os

import pytest
from pydantic import ValidationError
from sententia.config import SententiaConfig


class TestConfigContract:
    """Contract tests for sententia.config module."""

    def test_sententia_config_importable(self):
        """SententiaConfig must be importable from sententia.config."""
        assert SententiaConfig is not None

    def test_sententia_config_constructor_signature(self):
        """SententiaConfig must accept env_file and cli_overrides parameters."""
        sig = inspect.signature(SententiaConfig)
        params = sig.parameters
        assert "env_file" in params
        assert params["env_file"].default is None
        assert "cli_overrides" in params
        assert params["cli_overrides"].default is None

    def test_sententia_config_has_9_properties(self):
        """SententiaConfig must have 9 properties with correct types."""
        fields = SententiaConfig.model_fields
        expected = {
            "data_dir": "str",
            "index_path": "str",
            "llm_protocol": "str",
            "llm_url": "str",
            "llm_model": "str",
            "llm_token": "str",
            "mcp": "bool",
            "host": "str",
            "port": "int",
        }
        assert set(fields.keys()) == set(expected.keys()), (
            f"Properties mismatch: {set(fields.keys())} vs {set(expected.keys())}"
        )


class TestConfigDefaults:
    """Default values tests for SententiaConfig."""

    def test_config_defaults(self, monkeypatch):
        """In a clean environment, SententiaConfig returns all defaults."""
        for key in list(os.environ):
            if key.startswith("SENTENTIA_"):
                monkeypatch.delenv(key)

        config = SententiaConfig()

        assert config.data_dir == ""
        assert config.index_path is None
        assert config.llm_protocol == ""
        assert config.llm_url == ""
        assert config.llm_model == ""
        assert config.llm_token is None
        assert config.mcp is False
        assert config.host == "0.0.0.0"
        assert config.port == 8000


class TestConfigFromEnvVars:
    """ENV variable loading tests."""

    def test_config_from_env_vars(self, monkeypatch):
        """ENV variables with SENTENTIA_ prefix are loaded into config."""
        monkeypatch.setenv("SENTENTIA_LLM_PROTOCOL", "anthropic")
        monkeypatch.setenv("SENTENTIA_LLM_URL", "https://api.anthropic.com")
        monkeypatch.setenv("SENTENTIA_LLM_MODEL", "claude-3")

        config = SententiaConfig()

        assert config.llm_protocol == "anthropic"
        assert config.llm_url == "https://api.anthropic.com"
        assert config.llm_model == "claude-3"


class TestConfigCliOverrides:
    """CLI overrides priority tests."""

    def test_config_cli_overrides_take_priority(self, monkeypatch):
        """cli_overrides take priority over ENV variables."""
        monkeypatch.setenv("SENTENTIA_LLM_PROTOCOL", "anthropic")
        monkeypatch.setenv("SENTENTIA_HOST", "10.0.0.1")

        config = SententiaConfig(cli_overrides={"llm_protocol": "ollama", "host": "127.0.0.1"})

        assert config.llm_protocol == "ollama"
        assert config.host == "127.0.0.1"

    def test_config_none_cli_overrides(self, monkeypatch):
        """cli_overrides=None results in defaults."""
        for key in list(os.environ):
            if key.startswith("SENTENTIA_"):
                monkeypatch.delenv(key)

        config = SententiaConfig(cli_overrides=None)

        assert config.data_dir == ""
        assert config.host == "0.0.0.0"
        assert config.port == 8000

    def test_config_invalid_cli_overrides_type(self):
        """Invalid type in cli_overrides causes ValidationError."""
        with pytest.raises(ValidationError):
            SententiaConfig(cli_overrides={"port": "abc"})

    def test_config_none_values_in_overrides_do_not_overwrite_env(self, monkeypatch):
        """None values in cli_overrides should not overwrite ENV variables."""
        monkeypatch.setenv("SENTENTIA_LLM_TOKEN", "sk-from-env")

        config = SententiaConfig(cli_overrides={"llm_token": None})

        assert config.llm_token == "sk-from-env"

    def test_config_empty_cli_overrides(self, monkeypatch):
        """cli_overrides={} results in defaults."""
        for key in list(os.environ):
            if key.startswith("SENTENTIA_"):
                monkeypatch.delenv(key)

        config = SententiaConfig(cli_overrides={})

        assert config.host == "0.0.0.0"
        assert config.port == 8000


class TestConfigFromEnvFile:
    """Env-file loading tests."""

    def test_config_from_env_file(self, tmp_path, monkeypatch):
        """Values are loaded from the specified env-file."""
        for key in list(os.environ):
            if key.startswith("SENTENTIA_"):
                monkeypatch.delenv(key)

        env_path = tmp_path / ".env"
        env_path.write_text("SENTENTIA_LLM_TOKEN=sk-test-file\n")

        config = SententiaConfig(env_file=str(env_path))

        assert config.llm_token == "sk-test-file"


class TestConfigFullPriorityChain:
    """Full priority chain integration tests."""

    def test_config_full_priority_chain(self, tmp_path, monkeypatch):
        """Priority: cli_overrides > ENV > env-file > defaults."""
        monkeypatch.setenv("SENTENTIA_HOST", "10.0.0.1")
        monkeypatch.setenv("SENTENTIA_PORT", "9000")

        env_path = tmp_path / ".env"
        env_path.write_text("SENTENTIA_HOST=10.0.0.2\nSENTENTIA_LLM_TOKEN=sk-file\n")

        config = SententiaConfig(
            env_file=str(env_path),
            cli_overrides={"host": "127.0.0.1"},
        )

        assert config.host == "127.0.0.1"
        assert config.port == 9000
        assert config.llm_token == "sk-file"
