from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...endpoints import RESTResource
from .models import SearchRequest, SearchResponse, SearchResultItem

if TYPE_CHECKING:
    from sententia.index import Index


class SearchResource(RESTResource):
    """REST resource for semantic search over indexed documents."""

    url_rule = "/search"

    def __init__(self, index: Index, **kwargs: Any) -> None:
        """Initialize search resource.

        Args:
            index: Index instance for semantic search.
            **kwargs: Additional keyword arguments passed to RESTResource.
        """
        super().__init__(**kwargs)

        self._index = index

    def post(self, request: SearchRequest) -> SearchResponse:
        """Handle search request and return matching documents.

        Args:
            request: Search request with query and top-k parameter.

        Returns:
            Search response with ranked results.
        """
        raw = self._index.search(request.query, request.top)
        results = [SearchResultItem(text=item["text"],
                                    source=item["source"],
                                    score=item["score"]) for item in raw]

        return SearchResponse(results=results)
