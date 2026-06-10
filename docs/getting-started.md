# Getting Started

## Installation

Install Sententia and its dependencies:

```bash
pip install sententia
```

## Run with OpenAI

```bash
python -m sententia /path/to/markdown/docs \
  --llm-protocol openai \
  --llm-url https://api.openai.com \
  --llm-model gpt-4 \
  --llm-token sk-...
```

## Run with Ollama

Ollama works without an API key:

```bash
python -m sententia /path/to/markdown/docs \
  --llm-protocol ollama \
  --llm-url http://localhost:11434 \
  --llm-model llama3
```

## Run with Anthropic

```bash
python -m sententia /path/to/markdown/docs \
  --llm-protocol anthropic \
  --llm-url https://api.anthropic.com \
  --llm-model claude-3-sonnet \
  --llm-token sk-ant-...
```

## MCP Server Mode

Add the `--mcp` flag to start in MCP Server mode instead of REST API:

```bash
python -m sententia /path/to/markdown/docs \
  --llm-protocol ollama \
  --llm-url http://localhost:11434 \
  --llm-model llama3 \
  --mcp
```

## Configuration via .env file

Instead of passing all parameters via CLI, you can use a `.env` file:

```bash
# .env
SENTENTIA_LLM_PROTOCOL=ollama
SENTENTIA_LLM_URL=http://localhost:11434
SENTENTIA_LLM_MODEL=llama3
```

```bash
python -m sententia /path/to/markdown/docs
```

Use `--env-file` to specify a custom path:

```bash
python -m sententia /path/to/markdown/docs --env-file /path/to/config.env
```

See [Configuration](configuration.md) for all available environment variables and priority rules.

## First Request

After starting in REST mode:

### Search

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "how to set up authentication", "top": 5}'
```

### Ask (RAG)

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "how to set up authentication?"}'
```

### Files

```bash
curl http://localhost:8000/files/docs/auth.md
```