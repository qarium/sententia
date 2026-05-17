from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AskToolResult(BaseModel):
    model_config = ConfigDict(kw_only=True)

    answer: str = ""
    sources: list[str] = Field(default_factory=list)
