# AskResource — REST ресурс вопроса

## Назначение

`AskResource` — REST адаптер для RAG пайплайна (POST /ask).
Принимает AskRequest с запросом, вызывает rag.ask(), возвращает AskResponse с ответом и источниками.

## Использование

Создайте экземпляр с Index и LLM-провайдером, затем вызовите post():

```python
from sententia.api.ask import AskResource, AskRequest, AskResponse
from sententia.llm import OpenaiProvider

resource = AskResource(index=index, llm_provider=OpenaiProvider(url="...", model="llama3"))
response = resource.post(AskRequest(query="как настроить авторизацию?"))
print(response.answer)   # "Настройте OAuth2..."
print(response.sources)  # ["auth.md"]

# С явным указанием top
response = resource.post(AskRequest(query="как настроить авторизацию?", top=5))
```

## Параметры конструктора

- `index: Index` — экземпляр индекса для поиска
- `llm_provider: OpenaiProvider | AnthropicProvider` — LLM провайдер
- `top: int = 10` — количество результатов поиска по умолчанию (используется если в запросе top не указан)

## Параметры AskRequest

- `query: str` — текст вопроса (по умолчанию пустая строка)
- `top: int | None` — количество чанков для контекста. Если None — используется дефолт из конструктора

## Обработка ошибок

При ошибке LLM провайдера (LLMProviderError) выбрасывает HTTPException(502).