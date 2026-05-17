# FilesTool — MCP инструмент файлов

## Назначение

`FilesTool` — MCP инструмент для чтения содержимого файла по пути.

## Использование

Создайте экземпляр с Storage, затем вызовите execute():

```python
from sententia.mcp.files import FilesTool

tool = FilesTool(storage)
content = tool.execute(path="docs/auth.md")
# → {"text": "# Авторизация\n...", "source": "docs/auth.md"}
```

Если файл не найден — выбрасывается исключение (tool error).