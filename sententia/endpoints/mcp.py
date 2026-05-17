from typing import Any


class MCPTool:
    """Base class for MCP tools. Defines tool contract for MCP clients."""

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def description(self) -> str:
        raise NotImplementedError

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
