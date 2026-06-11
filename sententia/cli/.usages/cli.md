# CLI Arguments

Parse CLI arguments using parse_cli_args.

## Usage

```python
from sententia.cli import parse_cli_args

result = parse_cli_args()           # reads from sys.argv
result = parse_cli_args(["data"])   # reads from the provided list
```

## Result — ParseCliResult

Properties:
- data_dir: str — path to the Markdown files directory
- env_file: str | None — path to the env file
- index_path: str | None — path to the FAISS index file
- llm_protocol: str — LLM provider type
- llm_url: str — API endpoint URL
- llm_model: str — model identifier
- llm_token: str | None — API key
- mcp: bool | None — MCP Server mode flag
- host: str | None — bind address
- port: int | None — server port

## CLI Arguments

Positional:
  data_dir — path to the Markdown files directory

Options:
  --env-file — path to the env configuration file. Defaults to ".env" if not specified.
  --index-path — path to the FAISS index file
  --llm-protocol — LLM type (openai, anthropic, ollama). Required.
  --llm-url — API endpoint URL. Required.
  --llm-model — model identifier. Required.
  --llm-token — API key
  --mcp — run as MCP Server
  --host — bind address (default: 0.0.0.0)
  --port — server port (default: 8000)
