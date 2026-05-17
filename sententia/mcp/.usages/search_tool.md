# SearchTool — MCP инструмент поиска

## Назначение

`SearchTool` — MCP инструмент для семантического поиска документов.

## Использование

Создайте экземпляр с Index, затем вызовите execute():

```python
from sententia.index import Index
from sententia.mcp.search import SearchTool

index = Index(storage, "/data/index.faiss")
tool = SearchTool(index)
results = tool.execute(query="как настроить авторизацию", top=10)
# → [{"text": "...", "source": "docs/auth.md", "score": 0.95}, ...]
```