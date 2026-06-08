# Sententia

FastAPI-based search and RAG engine for local Markdown files, powered by FAISS and multilingual E5 embeddings.

**Documentation:** [qarium.github.io/sententia](https://qarium.github.io/sententia/)

## Quick Start

Install:

```bash
pip install sententia
```

Run with OpenAI-compatible LLM:

```bash
sententia /path/to/markdown/docs \
  --llm-protocol openai \
  --llm-url https://api.openai.com \
  --llm-model gpt-4o \
  --llm-token sk-...
```

Run with Anthropic:

```bash
sententia /path/to/markdown/docs \
  --llm-protocol anthropic \
  --llm-url https://api.anthropic.com \
  --llm-model claude-sonnet-4-6 \
  --llm-token sk-ant-...
```

Run with Ollama (no API key needed):

```bash
sententia /path/to/markdown/docs \
  --llm-protocol ollama \
  --llm-url http://localhost:11434 \
  --llm-model llama3
```

## Features

- **Semantic search** — FAISS index with `intfloat/multilingual-e5-base` embeddings
- **RAG Q&A** — retrieve relevant chunks and generate answers via LLM
- **Multiple LLM providers** — OpenAI, Anthropic, Ollama
- **Dual interface** — REST API server or MCP server (Model Context Protocol)
- **File access** — read original Markdown files by relative path

## Usage

```
sententia DATA_DIR [OPTIONS]
```

| Option           | Description                                           | Default      |
|------------------|-------------------------------------------------------|--------------|
| `DATA_DIR`       | Path to Markdown files directory                      | *(required)* |
| `--env-file`     | Path to env configuration file                        | `.env`       |
| `--index-path`   | Path to FAISS index file (persisted)                  | in-memory    |
| `--llm-protocol` | LLM provider: `openai`, `anthropic`, `ollama`         | *(required)* |
| `--llm-url`      | LLM API base URL (without `/v1` version path)         | *(required)* |
| `--llm-model`    | LLM model identifier                                  | *(required)* |
| `--llm-token`    | API key (falls back to `SENTENTIA_LLM_TOKEN` env var or env-file) | —            |
| `--host`         | Server bind address                                   | `0.0.0.0`    |
| `--port`         | Server port                                           | `8000`       |
| `--mcp`          | Run as MCP server instead of REST API                 | `false`      |

### Configuration

All settings can also be provided via environment variables with the `SENTENTIA_` prefix:

| Variable                 | Maps to        | Default      |
|--------------------------|----------------|--------------|
| `SENTENTIA_DATA_DIR`     | `data_dir`     | —            |
| `SENTENTIA_INDEX_PATH`   | `index_path`   | in-memory    |
| `SENTENTIA_LLM_PROTOCOL` | `llm_protocol` | *(required)* |
| `SENTENTIA_LLM_URL`      | `llm_url`      | *(required)* |
| `SENTENTIA_LLM_MODEL`    | `llm_model`    | *(required)* |
| `SENTENTIA_LLM_TOKEN`    | `llm_token`    | —            |
| `SENTENTIA_MCP`          | `mcp`          | `false`      |
| `SENTENTIA_HOST`         | `host`         | `0.0.0.0`    |
| `SENTENTIA_PORT`         | `port`         | `8000`       |

Settings can also be loaded from a `.env` file (default) or a custom file via `--env-file`.

**Priority:** CLI arguments > ENV variables > env-file > defaults.

## Reference

### REST API

**Search documents**

```
POST /search
```

```json
{ "query": "how to configure logging", "top": 10 }
```

Response:

```json
{
  "results": [
    { "text": "...", "source": "docs/guide.md", "score": 0.87 }
  ]
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `string` | `""` | Search query |
| `top` | `integer` | `10` | Number of results (1–100) |

**Ask a question (RAG)**

```
POST /ask
```

```json
{ "query": "how to configure logging" }
```

Response:

```json
{
  "answer": "To configure logging...",
  "sources": ["docs/guide.md", "docs/reference.md"]
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `string` | `""` | Question to answer |

**Read file**

```
GET /files/{path}
```

Response:

```json
{ "text": "file contents...", "source": "docs/guide.md" }
```

### MCP Tools

Launch with `--mcp` flag to expose tools via Model Context Protocol.

**`search`** — Search for relevant documents in the knowledge base.

| Parameter | Type      | Default | Description       |
|-----------|-----------|---------|-------------------|
| `query`   | `string`  | —       | Search query      |
| `top`     | `integer` | `10`    | Number of results |

Returns list of `{ text, source, score }`.

**`ask`** — Ask a question and get an answer based on indexed documents.

| Parameter | Type     | Default | Description        |
|-----------|----------|---------|--------------------|
| `query`   | `string` | —       | Question to answer |

Returns `{ answer, sources }`.

**`files`** — Read file content by path.

| Parameter | Type     | Default | Description        |
|-----------|----------|---------|--------------------|
| `path`    | `string` | —       | Relative file path |

Returns `{ text, source }`.

## Development

Clone and install with dev dependencies:

```bash
git clone https://github.com/qarium/sententia.git
cd sententia
pip install -e ".[test]"
```

Run tests:

```bash
pytest
```

Lint:

```bash
ruff check sententia tests
```