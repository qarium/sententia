# Application Parameters

Supply application parameters via command-line arguments (through the main routine) or environment variables.

Configuration is encapsulated in `SententiaConfig` from the `sententia/config` cell:

```python
from sententia.config import SententiaConfig

config = SententiaConfig(env_file=result.env_file, cli_overrides={...})
```

Precedence order: cli_overrides > ENV > env-file > defaults.

Required parameters:
  data_dir — path to the directory containing Markdown files
  llm_protocol — LLM provider type ("openai", "anthropic", "ollama")
  llm_url — API endpoint URL
  llm_model — model identifier

Optional parameters:
  index_path — path to the index file. When omitted, the index is built in memory without disk persistence
  llm_token — API key (not required for Ollama)
  mcp — MCP Server mode flag (default: False). When True, launches MCP Server instead of REST API
  host — bind address (default: 0.0.0.0)
  port — server port (default: 8000)
