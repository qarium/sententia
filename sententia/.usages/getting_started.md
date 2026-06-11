# Quick Start

Launch the service from the CLI:

```bash
python -m sententia /path/to/markdown/docs \
  --llm-protocol openai \
  --llm-url https://api.openai.com \
  --llm-model gpt-4 \
  --llm-token sk-...
```

Local launch via Ollama (no token required):

```bash
python -m sententia /path/to/markdown/docs \
  --llm-protocol ollama \
  --llm-url http://localhost:11434 \
  --llm-model llama3
```

Upon launch, the API is available at http://localhost:8000