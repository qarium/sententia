# Anthropic API — Text Generation via Claude Models

## Invoking the API via httpx

```python
import httpx

headers = {
    "x-api-key": token,
    "anthropic-version": "2023-06-01",
    "Content-Type": "application/json",
}
payload = {
    "model": model,
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 4096,
}

response = httpx.post(f"{url}/messages", json=payload, headers=headers)
response.raise_for_status()

answer = response.json()["content"][0]["text"]
```

## Parameters

- **Endpoint:** `POST {url}/messages` — the Messages API endpoint
- **Headers:** `x-api-key: {token}`, `anthropic-version: 2023-06-01`, `Content-Type: application/json`
- **Body:** `model`, `messages`, `max_tokens` (required), `system` — passed as a top-level field
- **Response:** `content[0].text` — `content` is an array of content blocks
- `token` is required for authentication