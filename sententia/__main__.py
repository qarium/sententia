from __future__ import annotations

import argparse
import os


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(prog="sententia", description="Sententia API server")
    parser.add_argument("data_dir", help="Path to Markdown files directory")
    parser.add_argument("--index-path", default=None, help="Path to FAISS index file")
    parser.add_argument(
        "--llm-protocol",
        required=True,
        choices=["openai", "anthropic", "ollama"],
        help="LLM provider protocol",
    )
    parser.add_argument("--llm-url", required=True, help="LLM API base URL (without /v1 version path)")
    parser.add_argument("--llm-model", required=True, help="LLM model identifier")
    parser.add_argument(
        "--llm-token",
        default=None,
        help="API key (not needed for Ollama). Falls back to SENTENTIA_LLM_TOKEN env var.",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Server bind address")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--mcp", action="store_true", default=False, help="Run as MCP Server instead of REST API")

    return parser


def main(argv: list[str] | None = None) -> None:
    """Entry point: parse args, create components, start server."""
    parser = build_parser()
    args = parser.parse_args(argv)

    token = args.llm_token or os.environ.get("SENTENTIA_LLM_TOKEN")

    from sententia.app import SententiaApp  # noqa: PLC0415
    from sententia.index import Index  # noqa: PLC0415
    from sententia.llm import AnthropicProvider, OpenaiProvider  # noqa: PLC0415
    from sententia.storage import Storage  # noqa: PLC0415

    storage = Storage(args.data_dir)
    index = Index(storage, args.index_path)

    if args.llm_protocol in ("openai", "ollama"):
        llm_provider = OpenaiProvider(args.llm_url, args.llm_model, token)
    else:
        llm_provider = AnthropicProvider(args.llm_url, args.llm_model, token)

    if args.mcp:
        from sententia.mcp import AskTool, FilesTool, SearchTool  # noqa: PLC0415

        search_tool = SearchTool(index)
        ask_tool = AskTool(index, llm_provider, top=10)
        files_tool = FilesTool(storage)

        app = SententiaApp()

        app.add_mcp_tool(search_tool)
        app.add_mcp_tool(ask_tool)
        app.add_mcp_tool(files_tool)

        app.run(host=args.host, port=args.port)
    else:
        from sententia.api import AskResource, FilesResource, SearchResource  # noqa: PLC0415

        search = SearchResource(index)
        ask_resource = AskResource(index, llm_provider, top=10)
        files = FilesResource(storage)

        app = SententiaApp()

        app.add_rest_resource(search)
        app.add_rest_resource(ask_resource)
        app.add_rest_resource(files)

        app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
