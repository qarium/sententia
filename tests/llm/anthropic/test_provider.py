from unittest import mock

import httpx
import pytest
from sententia.llm.anthropic import AnthropicProvider
from sententia.llm.provider import Provider
from sententia.llm.provider.errors import LLMProviderError

# --- Contract tests ---


def test_anthropic_provider_importable():
    assert AnthropicProvider is not None


def test_anthropic_provider_is_provider_subclass():
    assert issubclass(AnthropicProvider, Provider)


def test_anthropic_provider_has_generate():
    assert hasattr(AnthropicProvider, "generate")


# --- Logical tests ---


def test_anthropic_provider_generate_returns_answer():
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.is_success = True
    mock_response.json.return_value = {"content": [{"type": "text", "text": "ответ"}]}

    with mock.patch("httpx.post", return_value=mock_response):
        provider = AnthropicProvider("http://api.example.com", "claude-3", "tok123")
        result = provider.generate("hello")

    assert result == "ответ"


def test_anthropic_provider_sends_required_headers():
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.is_success = True
    mock_response.json.return_value = {"content": [{"type": "text", "text": "ok"}]}

    with mock.patch("httpx.post", return_value=mock_response) as mock_post:
        provider = AnthropicProvider("http://api.example.com", "claude-3", "tok123")
        provider.generate("hello")

    headers = mock_post.call_args.kwargs["headers"]
    assert headers["x-api-key"] == "tok123"
    assert headers["anthropic-version"] == "2023-06-01"


def test_anthropic_provider_sends_max_tokens():
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.is_success = True
    mock_response.json.return_value = {"content": [{"type": "text", "text": "ok"}]}

    with mock.patch("httpx.post", return_value=mock_response) as mock_post:
        provider = AnthropicProvider("http://api.example.com", "claude-3", "tok123")
        provider.generate("hello")

    body = mock_post.call_args.kwargs["json"]
    assert body["max_tokens"] == 4096


def test_anthropic_provider_url_appends_v1():
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.is_success = True
    mock_response.json.return_value = {"content": [{"type": "text", "text": "ok"}]}

    with mock.patch("httpx.post", return_value=mock_response) as mock_post:
        provider = AnthropicProvider("http://api.example.com", "claude-3", "tok123")
        provider.generate("hello")

    called_url = mock_post.call_args.args[0]
    assert called_url == "http://api.example.com/v1/messages"


def test_anthropic_provider_api_error():
    mock_response = mock.MagicMock()
    mock_response.status_code = 500
    mock_response.is_success = False
    mock_response.text = "Internal Server Error"

    with mock.patch("httpx.post", return_value=mock_response):
        provider = AnthropicProvider("http://api.example.com", "claude-3", "tok")
        with pytest.raises(LLMProviderError):
            provider.generate("hello")


def test_anthropic_provider_without_token_raises_error():
    provider = AnthropicProvider("http://api.example.com", "claude-3", None)
    with pytest.raises(LLMProviderError, match="requires an API key"):
        provider.generate("hello")


def test_anthropic_provider_network_error():
    with mock.patch("httpx.post", side_effect=httpx.ConnectError("Connection refused")):
        provider = AnthropicProvider("http://api.example.com", "claude-3", "tok")
        with pytest.raises(LLMProviderError, match="request failed"):
            provider.generate("hello")


def test_anthropic_provider_malformed_response():
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.is_success = True
    mock_response.json.return_value = {"content": []}
    mock_response.text = '{"content": []}'

    with mock.patch("httpx.post", return_value=mock_response):
        provider = AnthropicProvider("http://api.example.com", "claude-3", "tok")
        with pytest.raises(LLMProviderError, match=r"Unexpected.*response format"):
            provider.generate("hello")
