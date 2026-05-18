# LLM Providers

All providers implement a unified interface: `generate(prompt: str) -> str`.

## Base Interface

```python
class Provider:
    url: str           # Base API endpoint URL
    model: str         # Model identifier
    token: str | None  # API key (optional)

    def generate(self, prompt: str) -> str: ...
```

## OpenaiProvider

For OpenAI and Ollama (compatible API).

```python
from sententia.llm import OpenaiProvider

# OpenAI
provider = OpenaiProvider(
    url="https://api.openai.com",
    model="gpt-4",
    token="sk-..."
)

# Ollama (no token)
provider = OpenaiProvider(
    url="http://localhost:11434",
    model="llama3"
)
```

Calls `POST {url}/v1/chat/completions`. When `token is None`, no authorization header is sent (Ollama).

## AnthropicProvider

For Anthropic Claude.

```python
from sententia.llm import AnthropicProvider

provider = AnthropicProvider(
    url="https://api.anthropic.com",
    model="claude-3-sonnet",
    token="sk-ant-..."
)
```

Calls `POST {url}/v1/messages`. Token is required.

## Usage

```python
answer = provider.generate("Your prompt")
```

## Protocol Matching

| `--llm-protocol` | Provider | Token |
|-------------------|----------|-------|
| `openai` | `OpenaiProvider` | Required |
| `ollama` | `OpenaiProvider` | Not required |
| `anthropic` | `AnthropicProvider` | Required |