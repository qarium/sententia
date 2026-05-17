# MCP Reference

MCP Server доступен через Streamable HTTP transport на endpoint /mcp.
Клиент подключается через SSE к http://<host>:<port>/mcp.

## search
Поиск релевантных документов.
  Параметры: query: str, top: int = 10
  Результат: list[SearchToolResult] — [{"text": "...", "source": "file.md", "score": 0.95}, ...]

## ask
Вопрос-ответ с RAG.
  Параметры: query: str
  Результат: AskToolResult — {"answer": "...", "sources": ["file1.md", "file2.md"]}

## files
Чтение содержимого файла.
  Параметры: path: str
  Результат: FilesToolResult — {"text": "содержимое", "source": "path/to/file.md"}
  Ошибка: tool error если файл не найден
