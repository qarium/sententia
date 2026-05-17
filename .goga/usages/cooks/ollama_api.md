# Ollama — локальный LLM сервер

Протокол совместим с OpenAI API. Авторизация не требуется.

## Вызов через httpx

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

## Параметры

- Endpoint: `POST {url}/chat/completions` (обычно `http://localhost:11434/v1`)
- Headers: только `Content-Type: application/json`, без Authorization
- Body: `model` (имя из `ollama list`), `messages`, опционально `temperature`
- Ответ: `choices[0].message.content` — та же структура что у OpenAI
- token не нужен — авторизация отсутствует
- Если Ollama не запущен — ConnectionError
