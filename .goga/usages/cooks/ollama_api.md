# Ollama — Local LLM Server

The protocol is compatible with the OpenAI API. Authorization is not required.

## Invocation via httpx

```python
import httpx

headers = {
    "Content-Type": "application/json",
}
payload = {
    "model": model,
    "messages": [{"role": "user", "content": prompt}],
}

response = httpx.post(f"{url}/chat/completions", json=payload, headers=headers)
response.raise_for_status()

answer = response.json()["choices"][0]["message"]["content"]
```

## Parameters

- Endpoint: `POST {url}/chat/completions` (default base URL: `http://localhost:11434/v1`)
- Headers: `Content-Type: application/json` only — no `Authorization` header
- Body: `model` (string — model identifier from `ollama list`), `messages` (array of `{role, content}` objects), optional `temperature`
- Response: `choices[0].message.content` — identical to OpenAI response schema
- Authentication: not required — no token or API key needed
- Dependency: the Ollama service must be running. If unreachable, `httpx` raises a `ConnectionError`