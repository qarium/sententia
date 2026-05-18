# MCP Tools

The MCP Server is available when started with the `--mcp` flag. Transport: Streamable HTTP at the `/mcp` endpoint.

Clients connect via SSE to `http://<host>:<port>/mcp`.

## search

Semantic document search.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | — | Search query text |
| `top` | `int` | `10` | Number of results to return |

**Result:**

```json
[
  {
    "text": "Text fragment...",
    "source": "docs/auth.md",
    "score": 0.95
  }
]
```

## ask

Q&A with RAG pipeline.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | — | Question text |

**Result:**

```json
{
  "answer": "To set up authentication...",
  "sources": ["docs/auth.md", "docs/setup.md"]
}
```

## files

Read file content by path.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str` | — | Relative file path |

**Result:**

```json
{
  "text": "# Authentication\n\n...",
  "source": "docs/auth.md"
}
```

!!! error "File not found"
    Returns a tool error if the file is not found.