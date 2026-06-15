from __future__ import annotations

import inspect

import uvicorn
from fastapi import FastAPI

from ..endpoints import MCPTool, RESTResource


def _create_wrapper(tool: MCPTool):
    """Create a wrapper function for FastMCP registration with proper metadata."""

    def wrapper(**kwargs):
        return tool.execute(**kwargs)

    sig = inspect.signature(tool.execute)
    params = dict(sig.parameters)
    params.pop("self", None)
    wrapper.__signature__ = sig.replace(parameters=list(params.values()))  # type: ignore[attr-defined]
    wrapper.__name__ = tool.name
    wrapper.__doc__ = tool.description

    return wrapper


class SententiaApp:
    """Application container supporting REST API resources and MCP tool modes."""

    def __init__(self) -> None:
        self._app = FastAPI(title="Sententia API")
        self._resources: list[RESTResource] = []
        self._tools: list[MCPTool] = []
        self._mcp = None

    def add_rest_resource(self, resource: RESTResource) -> None:
        """Register a REST resource's route on the FastAPI application."""
        for method_name in ("get", "post", "put", "delete"):
            for cls in type(resource).__mro__:
                if cls is RESTResource:
                    break
                if method_name in cls.__dict__:
                    handler = getattr(resource, method_name)
                    self._app.add_api_route(resource.url_rule, handler, methods=[method_name.upper()])
                    break

        self._resources.append(resource)

    def add_mcp_tool(self, tool: MCPTool) -> None:
        """Register an MCP tool. FastMCP is created lazily on first call."""
        if self._mcp is None:  # type: ignore[has-type]
            from mcp.server.fastmcp import FastMCP  # noqa: PLC0415

            self._mcp = FastMCP("Sententia", json_response=True, stateless_http=True)

        wrapper = _create_wrapper(tool)

        self._mcp.tool()(wrapper)
        self._tools.append(tool)

    def run(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Run the application server. MCP mode if tools registered, FastAPI otherwise."""
        if self._tools and self._resources:
            raise RuntimeError("Cannot run with both tools and resources registered. Modes are mutually exclusive.")
        if self._tools:
            if self._mcp is None:
                raise RuntimeError("MCP server not initialized")

            self._mcp.settings.host = host
            self._mcp.settings.port = port
            self._mcp.run(transport="streamable-http")
        else:
            uvicorn.run(self._app, host=host, port=port)
