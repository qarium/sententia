# FilesTool — MCP File Reader Tool

## Purpose

`FilesTool` is an MCP tool that reads file contents by path using a `Storage` backend. It returns the file text and its source path.

## Usage

Instantiate with a `Storage` backend, then invoke `execute()`:

```python
from sententia.mcp.files import FilesTool

tool = FilesTool(storage)
content = tool.execute(path="docs/auth.md")
# → {"text": "# Authorization\n...", "source": "docs/auth.md"}
```

If the file at `path` does not exist, `FilesTool` raises a tool error exception.
