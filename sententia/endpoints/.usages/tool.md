# MCPTool — Abstract Base for MCP Tools

## Purpose

`MCPTool` is an abstract base class for MCP tools. It defines the contract for external MCP clients. Specialized by concrete implementations (SearchTool, AskTool, FilesTool).

## Usage

Subclass `MCPTool`, implementing properties `name`, `description` and method `execute`:

```python
class SearchTool(MCPTool):
    name = "search"
    description = "Search for relevant documents"

    def execute(self, query: str, top: int = 10) -> list[SearchToolResult]:
        # implementation
```

## Registration in MCP Server

To register a tool in FastMCP, create a wrapper function that delegates to the `execute` method and pass it to the `@mcp.tool()` decorator:

```python
from mcp.server.fastmcp import FastMCP
import inspect

mcp = FastMCP("MyServer")

tool = MyTool()  # MCPTool subclass instance

def wrapper(**kwargs):
    return tool.execute(**kwargs)

sig = inspect.signature(tool.execute)
params = dict(sig.parameters)
params.pop("self", None)
wrapper.__signature__ = sig.replace(parameters=list(params.values()))
wrapper.__name__ = tool.name
wrapper.__doc__ = tool.description

mcp.tool()(wrapper)
```

## Rules

- Base implementation of `execute()` raises NotImplementedError
- Properties `name` and `description` are required — tool identifier and description for MCP clients
- Override `execute()` with a concrete parameter signature
- Specialization pattern: concrete tool subclasses MCPTool, defines name/description, overrides execute()
