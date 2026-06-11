# API Reference

## POST /search
Search for relevant documents.

Request (SearchRequest):
```json
{"query": "text", "top": 10}
```

Response (SearchResponse):
```json
{"results": [{"text": "...", "source": "file.md", "score": 0.95}, ...]}
```

## POST /ask
Answer generation (RAG).

Request (AskRequest):
```json
{"query": "question text"}
```

Response (AskResponse):
```json
{"answer": "...", "sources": ["file1.md", "file2.md"]}
```

## GET /files/<path>
File contents.

Response (FileResponse):
```json
{"text": "contents", "source": "path/to/file.md"}
```

Error: returns 404 when the file is not found