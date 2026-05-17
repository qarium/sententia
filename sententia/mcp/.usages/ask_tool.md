# AskTool — MCP инструмент вопрос-ответ

## Назначение

`AskTool` — MCP инструмент для вопрос-ответ с RAG pipeline.

## Использование

Создайте экземпляр с Index и LLM-провайдером, затем вызовите execute():

```python
from sententia.mcp.ask import AskTool

tool = AskTool(index, llm_provider, top=10)
result = tool.execute(query="как настроить авторизацию?")
# → {"answer": "Для настройки...", "sources": ["docs/auth.md", "docs/setup.md"]}
```

## Обработка ошибок

При ошибке LLM провайдера (LLMProviderError) выбрасывается исключение (tool error).