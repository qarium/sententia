from unittest import mock

import httpx
import pytest
from sententia.llm.openai import OpenaiProvider
from sententia.llm.provider import Provider
from sententia.llm.provider.errors import LLMProviderError

# --- Contract tests ---


def test_openai_provider_importable():
    assert OpenaiProvider is not None


def test_openai_provider_is_provider_subclass():
    assert issubclass(OpenaiProvider, Provider)


def test_openai_provider_has_generate():
    assert hasattr(OpenaiProvider, "generate")


# --- Logical tests ---


def test_openai_provider_generate_with_token():
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.is_success = True
    mock_response.json.return_value = {"choices": [{"message": {"content": "ответ"}}]}

    with mock.patch("httpx.post", return_value=mock_response) as mock_post:
        provider = OpenaiProvider("http://api.example.com", "gpt-4", "tok123")
        result = provider.generate("hello")

    assert result == "ответ"
    call_kwargs = mock_post.call_args
    assert "Authorization" in call_kwargs.kwargs["headers"]
    assert call_kwargs.kwargs["headers"]["Authorization"] == "Bearer tok123"


def test_openai_provider_generate_without_token_ollama():
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.is_success = True
    mock_response.json.return_value = {"choices": [{"message": {"content": "ответ"}}]}

    with mock.patch("httpx.post", return_value=mock_response) as mock_post:
        provider = OpenaiProvider("http://localhost:11434", "llama3")
        result = provider.generate("hello")

    assert result == "ответ"
    call_kwargs = mock_post.call_args
    assert "Authorization" not in call_kwargs.kwargs["headers"]


def test_openai_provider_generate_api_error():
    mock_response = mock.MagicMock()
    mock_response.status_code = 500
    mock_response.is_success = False
    mock_response.text = "Internal Server Error"

    with mock.patch("httpx.post", return_value=mock_response):
        provider = OpenaiProvider("http://api.example.com", "gpt-4", "tok")
        with pytest.raises(LLMProviderError):
            provider.generate("hello")


def test_openai_provider_url_appends_v1():
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.is_success = True
    mock_response.json.return_value = {"choices": [{"message": {"content": "ok"}}]}

    with mock.patch("httpx.post", return_value=mock_response) as mock_post:
        provider = OpenaiProvider("http://api.example.com", "gpt-4", "tok")
        provider.generate("hello")

    called_url = mock_post.call_args.args[0]
    assert called_url == "http://api.example.com/v1/chat/completions"


def test_openai_provider_network_error():
    with mock.patch("httpx.post", side_effect=httpx.ConnectError("Connection refused")):
        provider = OpenaiProvider("http://api.example.com", "gpt-4", "tok")
        with pytest.raises(LLMProviderError, match="request failed"):
            provider.generate("hello")


def test_openai_provider_malformed_response():
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.is_success = True
    mock_response.json.return_value = {"choices": []}
    mock_response.text = '{"choices": []}'

    with mock.patch("httpx.post", return_value=mock_response):
        provider = OpenaiProvider("http://api.example.com", "gpt-4", "tok")
        with pytest.raises(LLMProviderError, match=r"Unexpected.*response format"):
            provider.generate("hello")
