# Configuration

Sententia can be configured via CLI arguments, environment variables, and `.env` files.

**Priority of sources** (highest to lowest):

1. **CLI arguments** — values passed via command line override everything
2. **Environment variables** — `SENTENTIA_*` variables
3. **`.env` file** — values loaded from an env-file
4. **Defaults** — built-in default values

## CLI Arguments

### Required

| Parameter | Description |
|-----------|-------------|
| `data_dir` | Positional argument — path to directory with Markdown files |
| `--llm-protocol` | LLM provider type: `openai`, `ollama`, `anthropic` |
| `--llm-url` | API endpoint URL |
| `--llm-model` | Model identifier |

### Optional

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--env-file` | `.env` | Path to env-file with configuration |
| `--index-path` | — | Path to index file. If not specified, index is built in memory |
| `--llm-token` | — | API key (not required for Ollama). Falls back to `SENTENTIA_LLM_TOKEN` |
| `--mcp` | `False` | MCP Server mode flag. When `True`, starts MCP Server instead of REST API |
| `--host` | `0.0.0.0` | Server bind address |
| `--port` | `8000` | Server port |

## Environment Variables

All environment variables use the `SENTENTIA_` prefix.

| Variable | Field | Default |
|----------|-------|---------|
| `SENTENTIA_DATA_DIR` | data_dir | `""` |
| `SENTENTIA_INDEX_PATH` | index_path | `None` |
| `SENTENTIA_LLM_PROTOCOL` | llm_protocol | `""` |
| `SENTENTIA_LLM_URL` | llm_url | `""` |
| `SENTENTIA_LLM_MODEL` | llm_model | `""` |
| `SENTENTIA_LLM_TOKEN` | llm_token | `None` |
| `SENTENTIA_MCP` | mcp | `False` |
| `SENTENTIA_HOST` | host | `"0.0.0.0"` |
| `SENTENTIA_PORT` | port | `8000` |

## Protocol Matching

| `--llm-protocol` | Provider | API |
|-------------------|----------|-----|
| `openai` | OpenaiProvider | `POST {url}/v1/chat/completions` |
| `ollama` | OpenaiProvider | `POST {url}/v1/chat/completions` (no auth) |
| `anthropic` | AnthropicProvider | `POST {url}/v1/messages` |

## Examples

### With persistent index

```bash
sententia /data/docs \
  --index-path /data/index.faiss \
  --llm-protocol openai \
  --llm-url https://api.openai.com \
  --llm-model gpt-4 \
  --llm-token "$OPENAI_API_KEY"
```

### In-memory index

```bash
sententia /data/docs \
  --llm-protocol ollama \
  --llm-url http://localhost:11434 \
  --llm-model llama3
```

### MCP Server

```bash
sententia /data/docs \
  --llm-protocol anthropic \
  --llm-url https://api.anthropic.com \
  --llm-model claude-3-sonnet \
  --mcp \
  --port 9000
```

### Using .env file

Create a `.env` file in the working directory:

```bash
SENTENTIA_LLM_PROTOCOL=openai
SENTENTIA_LLM_URL=https://api.openai.com
SENTENTIA_LLM_MODEL=gpt-4
SENTENTIA_LLM_TOKEN=sk-...
```

Run with minimal arguments:

```bash
sententia /data/docs
```

### Custom env-file path

```bash
sententia /data/docs --env-file /path/to/config.env
```