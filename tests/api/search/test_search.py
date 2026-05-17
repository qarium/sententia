from __future__ import annotations

from unittest.mock import MagicMock

from sententia.api.search import (
    SearchRequest,
    SearchResource,
    SearchResponse,
    SearchResultItem,
)
from sententia.endpoints import RESTResource


class TestSearchContract:
    def test_search_request_importable(self):
        assert SearchRequest is not None

    def test_search_result_item_importable(self):
        assert SearchResultItem is not None

    def test_search_response_importable(self):
        assert SearchResponse is not None

    def test_search_resource_importable(self):
        assert SearchResource is not None

    def test_search_resource_is_restresource_subclass(self):
        assert issubclass(SearchResource, RESTResource)

    def test_search_resource_has_post_method(self):
        assert hasattr(SearchResource, "post")

    def test_search_resource_url_rule(self):
        mock_index = MagicMock()
        resource = SearchResource(index=mock_index)
        assert resource.url_rule == "/search"


class TestSearchResourceLogic:
    def test_search_resource_post_returns_results(self):
        mock_index = MagicMock()
        mock_index.search.return_value = [
            {"text": "auth guide", "source": "auth.md", "score": 0.95},
        ]
        resource = SearchResource(index=mock_index)
        request = SearchRequest(query="auth", top=5)
        response = resource.post(request)

        assert isinstance(response, SearchResponse)
        assert len(response.results) == 1
        assert response.results[0].text == "auth guide"
        assert response.results[0].source == "auth.md"
        assert response.results[0].score == 0.95
        mock_index.search.assert_called_once_with("auth", 5)

    def test_search_resource_post_empty_results(self):
        mock_index = MagicMock()
        mock_index.search.return_value = []
        resource = SearchResource(index=mock_index)
        request = SearchRequest(query="nonexistent")
        response = resource.post(request)

        assert response.results == []

    def test_search_request_default_top(self):
        request = SearchRequest()
        assert request.top == 10

    def test_search_request_default_query(self):
        request = SearchRequest()
        assert request.query == ""
