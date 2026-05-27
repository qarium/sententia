# AskTool — MCP инструмент вопрос-ответ

## Назначение

`AskTool` — MCP инструмент для вопрос-ответ с RAG pipeline.

## Использование

Создайте экземпляр с Index и LLM-провайдером, затем вызовите execute():

```python
from sententia.mcp.ask import AskTool

tool = AskTool(index, llm_provider, top=10)
result = tool.execute(query="как настроить авторизацию?")
# → AskToolResult(answer="Для настройки...", sources=["docs/auth.md", "docs/setup.md"])

# С явным указанием top
result = tool.execute(query="как настроить авторизацию?", top=5)
```

## Обработка ошибок

При ошибке LLM провайдера (LLMProviderError) выбрасывается исключение (tool error).