from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SearchToolResult(BaseModel):
    """Single search result returned by MCP search tool."""

    model_config = ConfigDict(kw_only=True)

    text: str = ""
    source: str = ""
    score: float = 0.0
