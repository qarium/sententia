import pytest
from sententia.llm.provider import LLMProviderError, Provider

# --- Contract tests ---


def test_provider_importable():
    assert Provider is not None


def test_provider_has_generate_method():
    assert hasattr(Provider, "generate")


def test_provider_has_url_model_token_properties():
    assert hasattr(Provider, "url")
    assert hasattr(Provider, "model")
    assert hasattr(Provider, "token")


def test_llm_provider_error_importable():
    assert LLMProviderError is not None


def test_llm_provider_error_is_exception():
    assert issubclass(LLMProviderError, Exception)


# --- Logical tests ---


def test_provider_init_stores_config():
    provider = Provider("http://localhost:11434", "gpt-4", "tok123")
    assert provider.url == "http://localhost:11434"
    assert provider.model == "gpt-4"
    assert provider.token == "tok123"


def test_provider_token_default_none():
    provider = Provider("http://localhost:11434", "gpt-4")
    assert provider.token is None


def test_provider_generate_raises_not_implemented():
    provider = Provider("http://localhost:11434", "gpt-4")
    with pytest.raises(NotImplementedError):
        provider.generate("test prompt")
