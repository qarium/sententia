# REST API

The REST API is available when started without the `--mcp` flag. Base URL: `http://localhost:8000`.

## POST /search

Semantic search for relevant documents.

**Request:**

```json
{
  "query": "how to set up authentication",
  "top": 10
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | `str` | `""` | Search query text |
| `top` | `int` | `10` | Number of results to return |

**Response:**

```json
{
  "results": [
    {
      "text": "Document text fragment...",
      "source": "docs/auth.md",
      "score": 0.95
    }
  ]
}
```

Results are sorted by `score` descending (cosine similarity).

## POST /ask

Answer generation based on RAG (search + LLM).

**Request:**

```json
{
  "query": "how to set up authentication?",
  "top": 5
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | `str` | `""` | User question text |
| `top` | `int \| null` | `null` | Number of context chunks for RAG. Falls back to server default |

**Response:**

```json
{
  "answer": "To set up authentication...",
  "sources": ["docs/auth.md", "docs/setup.md"]
}
```

If the context is insufficient, the answer will contain: `"Insufficient data to answer this question"`.

!!! warning "LLM Error"
    Returns HTTP 502 on LLM provider failure.

## GET /files/{path}

Get file content by relative path.

**Response:**

```json
{
  "text": "# Authentication\n\n...",
  "source": "docs/auth.md"
}
```

| Code | Description |
|------|-------------|
| 200 | File found |
| 404 | File not found or path traversal |
| 403 | Permission denied |