# Configuration

Application parameters are passed via command-line arguments.

## Required Parameters

| Parameter | Description |
|-----------|-------------|
| `data_dir` | Positional argument — path to directory with Markdown files |
| `--llm-protocol` | LLM provider type: `openai`, `ollama`, `anthropic` |
| `--llm-url` | API endpoint URL |
| `--llm-model` | Model identifier |

## Optional Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--index-path` | — | Path to index file. If not specified, index is built in memory |
| `--llm-token` | — | API key (not required for Ollama) |
| `--mcp` | `False` | MCP Server mode flag. When `True`, starts MCP Server instead of REST API |
| `--host` | `0.0.0.0` | Server bind address |
| `--port` | `8000` | Server port |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SENTENTIA_LLM_TOKEN` | Sets the token for LLM access |

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