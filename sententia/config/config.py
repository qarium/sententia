from __future__ import annotations


class SententiaConfig:
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

    pass
