# MCP Reference

The MCP Server exposes a Streamable HTTP transport on the /mcp endpoint.
Clients connect via SSE at http://<host>:<port>/mcp.

## search
Retrieve relevant documents.
  Parameters: query: str, top: int = 10
  Result: `list[SearchToolResult]` — `[{"text": "...", "source": "file.md", "score": 0.95}, ...]`

## ask
Answer questions using RAG.
  Parameters: query: str
  Result: `AskToolResult` — `{"answer": "...", "sources": ["file1.md", "file2.md"]}`

## files
Read file contents.
  Parameters: path: str
  Result: `FilesToolResult` — `{"text": "contents", "source": "path/to/file.md"}`
  Error: returns a tool error when the file is not found
