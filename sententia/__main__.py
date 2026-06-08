from __future__ import annotations


def main(argv: list[str] | None = None) -> None:
    """Entry point: parse args, create config, assemble components, start server.

    Args:
        argv: List of CLI arguments. None means use sys.argv.
    """
    from sententia.cli import parse_cli_args  # noqa: PLC0415
    from sententia.config import SententiaConfig  # noqa: PLC0415

    result = parse_cli_args(argv)

    cli_overrides = {
        k: v
        for k, v in {
            "data_dir": result.data_dir,
            "index_path": result.index_path,
            "llm_protocol": result.llm_protocol,
            "llm_url": result.llm_url,
            "llm_model": result.llm_model,
            "llm_token": result.llm_token,
            "mcp": result.mcp,
            "host": result.host,
            "port": result.port,
        }.items()
        if v is not None
    }

    config = SententiaConfig(env_file=result.env_file, cli_overrides=cli_overrides)

    from sententia.app import SententiaApp  # noqa: PLC0415
    from sententia.index import Index  # noqa: PLC0415
    from sententia.llm import AnthropicProvider, OpenaiProvider  # noqa: PLC0415
    from sententia.storage import Storage  # noqa: PLC0415

    storage = Storage(config.data_dir)
    index = Index(storage, config.index_path)

    if config.llm_protocol in ("openai", "ollama"):
        llm_provider = OpenaiProvider(config.llm_url, config.llm_model, config.llm_token)
    elif config.llm_protocol == "anthropic":
        llm_provider = AnthropicProvider(config.llm_url, config.llm_model, config.llm_token)
    else:
        raise ValueError(f"Unknown LLM protocol: {config.llm_protocol}")

    if config.mcp:
        from sententia.mcp import AskTool, FilesTool, SearchTool  # noqa: PLC0415

        search_tool = SearchTool(index)
        ask_tool = AskTool(index, llm_provider, top=10)
        files_tool = FilesTool(storage)

        app = SententiaApp()

        app.add_mcp_tool(search_tool)
        app.add_mcp_tool(ask_tool)
        app.add_mcp_tool(files_tool)

        app.run(host=config.host, port=config.port)
    else:
        from sententia.api import AskResource, FilesResource, SearchResource  # noqa: PLC0415

        search = SearchResource(index)
        ask_resource = AskResource(index, llm_provider, top=10)
        files = FilesResource(storage)

        app = SententiaApp()

        app.add_rest_resource(search)
        app.add_rest_resource(ask_resource)
        app.add_rest_resource(files)

        app.run(host=config.host, port=config.port)


if __name__ == "__main__":
    main()
