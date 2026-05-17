from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...endpoints import RESTResource
from .models import SearchRequest, SearchResponse, SearchResultItem

if TYPE_CHECKING:
    from sententia.index import Index


class SearchResource(RESTResource):
    url_rule = "/search"

    def __init__(self, index: Index, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._index = index

    def post(self, request: SearchRequest) -> SearchResponse:
        raw = self._index.search(request.query, request.top)
        results = [SearchResultItem(text=item["text"], source=item["source"], score=item["score"]) for item in raw]
        return SearchResponse(results=results)
