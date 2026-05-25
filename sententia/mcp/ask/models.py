from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AskToolResult(BaseModel):
    """Result returned by MCP ask tool with answer and source references."""

    model_config = ConfigDict(kw_only=True)

    answer: str = ""
    sources: list[str] = Field(default_factory=list)
