# Anthropic API — генерация текста через Claude-модели

## Вызов через httpx

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

## Параметры

- Endpoint: `POST {url}/messages`
- Headers: `x-api-key: {token}`, `anthropic-version: 2023-06-01`, `Content-Type: application/json`
- Body: `model`, `messages`, `max_tokens` (обязательный!), `system` — отдельным полем
- Ответ: `content[0].text` (content — массив блоков)
- token обязателен
