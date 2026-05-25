from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SearchRequest(BaseModel):
    """Request body for semantic search."""

    model_config = ConfigDict(kw_only=True)

    query: str = ""
    top: int = Field(default=10, ge=1, le=100)


class SearchResultItem(BaseModel):
    """Single search result with text, source, and relevance score."""

    model_config = ConfigDict(kw_only=True)

    text: str = ""
    source: str = ""
    score: float = 0.0


class SearchResponse(BaseModel):
    """Response body containing search results."""

    model_config = ConfigDict(kw_only=True)

    results: list[SearchResultItem] = Field(default_factory=list)
