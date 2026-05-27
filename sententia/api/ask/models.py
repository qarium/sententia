from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AskRequest(BaseModel):
    """Request body for RAG question answering."""

    model_config = ConfigDict(kw_only=True)

    query: str = ""
    top: int | None = None


class AskResponse(BaseModel):
    """Response body with generated answer and source references."""

    model_config = ConfigDict(kw_only=True)

    answer: str = ""
    sources: list[str] = Field(default_factory=list)
