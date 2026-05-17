from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sententia.api.ask import AskRequest, AskResource, AskResponse
from sententia.endpoints import RESTResource
from sententia.llm.provider.errors import LLMProviderError


class TestAskContract:
    def test_ask_request_importable(self):
        assert AskRequest is not None

    def test_ask_response_importable(self):
        assert AskResponse is not None

    def test_ask_resource_importable(self):
        assert AskResource is not None

    def test_ask_resource_is_restresource_subclass(self):
        assert issubclass(AskResource, RESTResource)

    def test_ask_resource_url_rule(self):
        mock_index = MagicMock()
        mock_provider = MagicMock()
        resource = AskResource(index=mock_index, llm_provider=mock_provider)
        assert resource.url_rule == "/ask"


class TestAskResourceLogic:
    def test_ask_resource_post_returns_answer(self, monkeypatch):
        mock_index = MagicMock()
        mock_provider = MagicMock()
        mock_rag = MagicMock()
        mock_rag.ask.return_value = {
            "answer": "Настройте OAuth2",
            "sources": ["auth.md"],
        }
        monkeypatch.setattr("sententia.api.ask.ask.rag", mock_rag)

        resource = AskResource(index=mock_index, llm_provider=mock_provider)
        request = AskRequest(query="Как настроить авторизацию?")
        response = resource.post(request)

        assert isinstance(response, AskResponse)
        assert response.answer == "Настройте OAuth2"
        assert response.sources == ["auth.md"]

    def test_ask_resource_post_llm_error_returns_502(self, monkeypatch):
        mock_index = MagicMock()
        mock_provider = MagicMock()
        mock_rag = MagicMock()
        mock_rag.ask.side_effect = LLMProviderError("API error")
        monkeypatch.setattr("sententia.api.ask.ask.rag", mock_rag)

        resource = AskResource(index=mock_index, llm_provider=mock_provider)
        request = AskRequest(query="test")

        with pytest.raises(HTTPException) as exc_info:
            resource.post(request)
        assert exc_info.value.status_code == 502

    def test_ask_resource_default_top(self):
        mock_index = MagicMock()
        mock_provider = MagicMock()
        resource = AskResource(index=mock_index, llm_provider=mock_provider)
        assert resource._top == 10
