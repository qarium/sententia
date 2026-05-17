from __future__ import annotations

import importlib

__all__ = [
    "AnthropicProvider",
    "AskRequest",
    "AskResource",
    "AskResponse",
    "AskTool",
    "FileResponse",
    "FilesResource",
    "FilesTool",
    "Index",
    "MCPTool",
    "OpenaiProvider",
    "RESTResource",
    "SearchRequest",
    "SearchResource",
    "SearchResponse",
    "SearchResultItem",
    "SearchTool",
    "SententiaApp",
    "Storage",
    "ask",
]

_LAZY_MODULES = {
    "RESTResource": ("sententia.endpoints", "RESTResource"),
    "MCPTool": ("sententia.endpoints", "MCPTool"),
    "SententiaApp": ("sententia.app", "SententiaApp"),
    "Index": ("sententia.index", "Index"),
    "OpenaiProvider": ("sententia.llm", "OpenaiProvider"),
    "AnthropicProvider": ("sententia.llm", "AnthropicProvider"),
    "Storage": ("sententia.storage", "Storage"),
    "ask": ("sententia.rag", "ask"),
    "SearchResource": ("sententia.api", "SearchResource"),
    "AskResource": ("sententia.api", "AskResource"),
    "FilesResource": ("sententia.api", "FilesResource"),
    "SearchRequest": ("sententia.api.search", "SearchRequest"),
    "SearchResponse": ("sententia.api.search", "SearchResponse"),
    "SearchResultItem": ("sententia.api.search", "SearchResultItem"),
    "AskRequest": ("sententia.api.ask", "AskRequest"),
    "AskResponse": ("sententia.api.ask", "AskResponse"),
    "FileResponse": ("sententia.api.files", "FileResponse"),
    "SearchTool": ("sententia.mcp", "SearchTool"),
    "AskTool": ("sententia.mcp", "AskTool"),
    "FilesTool": ("sententia.mcp", "FilesTool"),
}


def __getattr__(name: str):
    if name in _LAZY_MODULES:
        module_path, attr = _LAZY_MODULES[name]
        mod = importlib.import_module(module_path)
        value = getattr(mod, attr)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
