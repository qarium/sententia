from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...endpoints import MCPTool
from .models import SearchToolResult

if TYPE_CHECKING:
    from sententia.index import Index


class SearchTool(MCPTool):
    """MCP tool for semantic search over indexed documents."""

    name = "search"
    description = "Search for relevant documents in the knowledge base"

    def __init__(self, index: Index, **kwargs: Any) -> None:
        """Initialize search tool.

        Args:
            index: Index instance for semantic search.
            **kwargs: Additional keyword arguments passed to MCPTool.
        """
        super().__init__(**kwargs)

        self._index = index

    def execute(self, query: str, top: int = 10) -> list[SearchToolResult]:
        """Execute semantic search and return matching documents.

        Args:
            query: Search query text.
            top: Number of top results to return.

        Returns:
            List of search results with text, source, and score.
        """
        raw = self._index.search(query, top)

        return [SearchToolResult(text=item["text"], source=item["source"], score=item["score"]) for item in raw]
