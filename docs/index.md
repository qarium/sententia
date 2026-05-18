# Sententia

FastAPI-based search and RAG engine for local Markdown files.

Sententia indexes Markdown files using FAISS + Sentence-Transformers and provides two access modes:

- **REST API** — HTTP endpoints for search, Q&A (RAG), and file reading
- **MCP Server** — tools for integration with MCP clients

## Features

- Semantic search over indexed documents
- RAG pipeline — answer generation based on relevant chunks
- OpenAI, Ollama, and Anthropic as LLM providers
- Persistent and in-memory indexing modes
- File content reading by path

## Quick Start

```bash
python -m sententia /path/to/markdown/docs \
  --llm-protocol openai \
  --llm-url https://api.openai.com \
  --llm-model gpt-4 \
  --llm-token sk-...
```

??? note "Local run with Ollama (no token required)"
    ```bash
    python -m sententia /path/to/markdown/docs \
      --llm-protocol ollama \
      --llm-url http://localhost:11434 \
      --llm-model llama3
    ```

Once started, the API is available at `http://localhost:8000`.

## Sections

- [:material-play: Getting Started](getting-started.md) — launch and first request
- [:material-cog: Configuration](configuration.md) — CLI parameters and environment variables
- [:material-api: REST API](rest-api.md) — HTTP endpoints
- [:material-tools: MCP Tools](mcp-tools.md) — tools for MCP clients
- [:material-database: Core Concepts](storage.md) — internal components