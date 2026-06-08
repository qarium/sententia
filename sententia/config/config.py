from __future__ import annotations

from typing import Any

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SententiaConfig(BaseSettings):
    """Application configuration model.

    Loads values from ENV variables with prefix SENTENTIA_ and from env-file.
    Priority: cli_overrides > ENV > env-file > defaults.

    Attributes:
        data_dir: Path to the Markdown files directory.
        index_path: Path to the FAISS index file. None means in-memory index.
        llm_protocol: LLM provider type (openai, anthropic, ollama).
        llm_url: URL of the LLM API endpoint.
        llm_model: Identifier of the LLM model.
        llm_token: API key. None means token not needed (Ollama).
        mcp: MCP Server mode flag. Defaults to False.
        host: Server bind address. Defaults to "0.0.0.0".
        port: Server port. Defaults to 8000.
    """

    model_config = SettingsConfigDict(
        env_prefix="SENTENTIA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    data_dir: str = ""
    index_path: str | None = None
    llm_protocol: str = ""
    llm_url: str = ""
    llm_model: str = ""
    llm_token: str | None = Field(None, repr=False)
    mcp: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    def __init__(
        self,
        env_file: str | None = None,
        cli_overrides: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize SententiaConfig.

        Args:
            env_file: Path to env configuration file. None means use ".env".
            cli_overrides: Dict of CLI values to override ENV/env-file.
            **kwargs: Additional field values.
        """
        if env_file is not None:
            kwargs["_env_file"] = env_file
        if cli_overrides is not None:
            kwargs["cli_overrides"] = cli_overrides
        super().__init__(**kwargs)

    @model_validator(mode="before")
    @classmethod
    def apply_overrides(cls, values: dict) -> dict:
        """Apply CLI overrides on top of ENV/env-file values."""
        overrides = values.pop("cli_overrides", None) or {}
        values.update({k: v for k, v in overrides.items() if v is not None})
        return values
