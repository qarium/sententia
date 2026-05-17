# OpenAI API — генерация текста через GPT-модели

## Вызов через httpx

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

## Параметры

- Endpoint: `POST {url}/chat/completions`
- Headers: `Authorization: Bearer {token}`, `Content-Type: application/json`
- Body: `model`, `messages` (массив `{role, content}`), опционально `temperature`, `max_tokens`
- Ответ: `choices[0].message.content`
- token обязателен — без него API вернёт 401
