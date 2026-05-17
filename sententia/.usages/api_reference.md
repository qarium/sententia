# API Reference

## POST /search
Поиск релевантных документов.
  Request (SearchRequest):  {"query": "текст", "top": 10}
  Response (SearchResponse): {"results": [{"text": "...", "source": "file.md", "score": 0.95}, ...]}

## POST /ask
Генерация ответа (RAG).
  Request (AskRequest):  {"query": "текст вопроса"}
  Response (AskResponse): {"answer": "...", "sources": ["file1.md", "file2.md"]}

## GET /files/<path>
Содержимое файла.
  Response (FileResponse): {"text": "содержимое", "source": "path/to/file.md"}
  Ошибка: 404 если файл не найден