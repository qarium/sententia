from __future__ import annotations

import argparse
import sys

from pydantic import BaseModel, ConfigDict


class ParseCliResult(BaseModel):
    """Data model for CLI argument parsing results.

    Contains all parsed values and the path to the env file.

    Attributes:
        data_dir: Path to the Markdown files directory.
        env_file: Path to the env configuration file. None means use default.
        index_path: Path to the FAISS index file. None means in-memory index.
        llm_protocol: LLM provider type (openai, anthropic, ollama).
        llm_url: URL of the LLM API endpoint.
        llm_model: Identifier of the LLM model.
        llm_token: API key. None means get from ENV or env-file.
        mcp: MCP Server mode flag. None means not specified (use config default).
        host: Server bind address. None means not specified (use config default).
        port: Server port. None means not specified (use config default).
    """

    model_config = ConfigDict(kw_only=True)

    data_dir: str
    env_file: str | None = None
    index_path: str | None = None
    llm_protocol: str
    llm_url: str
    llm_model: str
    llm_token: str | None = None
    mcp: bool | None = None
    host: str | None = None
    port: int | None = None


def parse_cli_args(argv: list[str] | None = None) -> ParseCliResult:
    """Parse CLI arguments.

    Args:
        argv: List of arguments. None means use sys.argv.

    Returns:
        ParseCliResult with parsed values.
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog="sententia")

    parser.add_argument("data_dir", help="Path to Markdown files directory")
    parser.add_argument("--env-file", default=None, help="Path to env configuration file")
    parser.add_argument("--index-path", default=None, help="Path to FAISS index file")
    parser.add_argument(
        "--llm-protocol",
        required=True,
        choices=["openai", "anthropic", "ollama"],
        help="LLM provider type",
    )
    parser.add_argument("--llm-url", required=True, help="LLM API endpoint URL")
    parser.add_argument("--llm-model", required=True, help="LLM model identifier")
    parser.add_argument("--llm-token", default=None, help="API key")
    parser.add_argument("--mcp", action="store_true", default=None, help="Run as MCP Server")
    parser.add_argument("--host", default=None, help="Server bind address")
    parser.add_argument("--port", type=int, default=None, help="Server port")

    args = parser.parse_args(argv)

    return ParseCliResult(
        data_dir=args.data_dir,
        env_file=args.env_file,
        index_path=args.index_path,
        llm_protocol=args.llm_protocol,
        llm_url=args.llm_url,
        llm_model=args.llm_model,
        llm_token=args.llm_token,
        mcp=args.mcp,
        host=args.host,
        port=args.port,
    )
