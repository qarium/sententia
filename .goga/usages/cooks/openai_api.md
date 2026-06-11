# OpenAI API — Text Generation via GPT Models

## Invocation via httpx

```python
import httpx

headers = {
    "Authorization": f"Bearer {token}",
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

- Endpoint: `POST {url}/chat/completions`
- Headers: `Authorization: Bearer {token}` (required), `Content-Type: application/json`
- Body: `model` (string — GPT model identifier), `messages` (array of `{role, content}` objects), optional `temperature`, `max_tokens`
- Response: `choices[0].message.content`
- Authentication: required — requests without a valid token receive `401 Unauthorized`