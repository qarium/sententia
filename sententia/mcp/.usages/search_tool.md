# SearchTool — MCP Semantic Search Tool

## Purpose

`SearchTool` is an MCP tool that performs semantic document search using an `Index`. It retrieves documents matching a query and returns ranked results with text, source, and relevance score.

## Usage

Instantiate with an `Index`, then invoke `execute()`:

```python
from sententia.index import Index
from sententia.mcp.search import SearchTool

index = Index(storage, "/data/index.faiss")
tool = SearchTool(index)
results = tool.execute(query="how to configure authorization", top=10)
# → [{"text": "...", "source": "docs/auth.md", "score": 0.95}, ...]
```
