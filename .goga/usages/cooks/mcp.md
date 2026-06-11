# MCP Python SDK

## Purpose

The `mcp` library is the official Anthropic Python SDK for building MCP (Model Context Protocol) servers and clients.
It exposes tools to external MCP clients (Claude Desktop, Cursor, and others).

**Package:** `mcp>=1.27.0`

## Key Components

### FastMCP

A high-level server class for rapid MCP server creation.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="ServerName",
    instructions="Server description for clients",
    json_response=True,       # JSON instead of SSE where possible
    stateless_http=True,      # no sticky sessions, simpler deployment
)
```

### Tool Definition

Register tools via `mcp.tool()`. The function's type annotations drive automatic JSON Schema generation for clients.

#### Decorator-Based Registration

```python
@mcp.tool()
def search(query: str, limit: int = 10) -> list[str]:
    """Search the knowledge base."""
    return ["result-1", "result-2"]

@mcp.tool()
async def ask(question: str) -> str:
    """RAG-based question answering."""
    return "answer"
```

#### Programmatic Registration of an Existing Method

Invoke `mcp.tool()` as a function and pass a callable directly — without decorator syntax.
This pattern registers bound methods from existing objects through a wrapper function:

```python
class MyTool:
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "Tool description"

    def execute(self, query: str, top: int = 5) -> list[str]:
        return ["result"]

tool = MyTool()

# Build a wrapper function for FastMCP registration
def _make_wrapper(t):
    def wrapper(query: str, top: int = 5) -> list[str]:
        return t.execute(query, top)
    wrapper.__name__ = t.name
    wrapper.__doc__ = t.description
    return wrapper

mcp.tool(_make_wrapper(tool))
```

Wrapper function requirements:
- Set `__name__` to the tool name exposed in the MCP protocol
- Set `__doc__` to the tool description — FastMCP reads the docstring as the MCP description field
- Preserve type annotations on all parameters — FastMCP derives the JSON Schema from the signature
- Delegate to `tool.execute()` with the matching arguments

#### General Rules

- The docstring becomes the tool description in the MCP protocol
- Both sync and async functions are supported
- Return types — Pydantic models, TypedDict, dataclasses, and built-in collections — are serialized automatically

### Standalone Server (Streamable HTTP)

Streamable HTTP is the recommended transport. Start the server as a standalone process via `mcp.run()`.

```python
mcp = FastMCP("ServerName", stateless_http=True, json_response=True)

# ... tool definitions ...

# Start as a standalone ASGI server
mcp.run(transport="streamable-http")
```

Calling `mcp.run(transport="streamable-http")` starts the built-in ASGI server (uvicorn). Configuration options:

```python
mcp.settings.host = "127.0.0.1"  # host
mcp.settings.port = 8000          # port
```

## FastMCP Constructor

| Parameter | Default | Description |
|---|---|---|
| `name` | required | Server name in the MCP protocol |
| `instructions` | `None` | Human-readable server description |
| `host` | `"127.0.0.1"` | Host for standalone server |
| `port` | `8000` | Port for standalone server |
| `json_response` | `False` | Use JSON responses instead of SSE |
| `stateless_http` | `False` | Stateless mode — no sticky sessions |
| `streamable_http_path` | `"/mcp"` | URL path for Streamable HTTP transport |