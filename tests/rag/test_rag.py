from __future__ import annotations

import inspect
from unittest.mock import MagicMock

from sententia.llm import AnthropicProvider, OpenaiProvider
from sententia.rag import ask

# --- Contract tests ---


class TestContractAskImportable:
    def test_ask_importable(self):
        assert callable(ask)


class TestContractAskSignature:
    def test_ask_signature(self):
        sig = inspect.signature(ask)
        params = list(sig.parameters.keys())
        assert params == ["query", "index", "llm_provider", "top"]
        assert sig.parameters["top"].default == 10

    def test_ask_accepts_openai_provider(self):
        mock_index = MagicMock()
        mock_index.search.return_value = []
        mock_provider = MagicMock(spec=OpenaiProvider)
        mock_provider.generate.return_value = "Ответ"

        result = ask("question", mock_index, mock_provider)

        assert result["answer"] == "Ответ"

    def test_ask_accepts_anthropic_provider(self):
        mock_index = MagicMock()
        mock_index.search.return_value = []
        mock_provider = MagicMock(spec=AnthropicProvider)
        mock_provider.generate.return_value = "Ответ"

        result = ask("question", mock_index, mock_provider)

        assert result["answer"] == "Ответ"

    def test_ask_top_default_is_10(self):
        sig = inspect.signature(ask)
        assert sig.parameters["top"].default == 10


# --- Logic tests ---


class TestAskReturnsAnswerWithSources:
    def test_ask_returns_answer_with_sources(self):
        mock_index = MagicMock()
        mock_index.search.return_value = [{"text": "chunk", "source": "doc.md", "score": 0.9}]
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Ответ"

        result = ask("question", mock_index, mock_llm)

        assert result["answer"] == "Ответ"
        assert result["sources"] == ["doc.md"]
        prompt_arg = mock_llm.generate.call_args[0][0]
        assert "Недостаточно данных" in prompt_arg

    def test_ask_uses_default_top(self):
        mock_index = MagicMock()
        mock_index.search.return_value = []
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Ответ"

        ask("query", mock_index, mock_llm)

        mock_index.search.assert_called_once_with("query", 10)


class TestAskEmptySearchResults:
    def test_ask_empty_search_results(self):
        mock_index = MagicMock()
        mock_index.search.return_value = []
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Недостаточно данных для ответа на данный вопрос"

        result = ask("question", mock_index, mock_llm)

        assert result["answer"] == "Недостаточно данных для ответа на данный вопрос"
        assert result["sources"] == []


class TestAskCustomTop:
    def test_ask_custom_top(self):
        mock_index = MagicMock()
        mock_index.search.return_value = [
            {"text": "Chunk", "source": "doc.md", "score": 0.9},
        ]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Answer"

        ask("query", mock_index, mock_llm, top=3)

        mock_index.search.assert_called_once_with("query", 3)


class TestAskWithOpenaiProvider:
    def test_ask_with_openai_provider(self):
        mock_index = MagicMock()
        mock_index.search.return_value = [{"text": "auth guide", "source": "auth.md", "score": 0.95}]
        mock_provider = MagicMock(spec=OpenaiProvider)
        mock_provider.generate.return_value = "Настройте OAuth2"

        result = ask("How to auth?", mock_index, mock_provider)

        assert result["answer"] == "Настройте OAuth2"
        assert result["sources"] == ["auth.md"]


class TestAskWithAnthropicProvider:
    def test_ask_with_anthropic_provider(self):
        mock_index = MagicMock()
        mock_index.search.return_value = [{"text": "deploy guide", "source": "deploy.md", "score": 0.88}]
        mock_provider = MagicMock(spec=AnthropicProvider)
        mock_provider.generate.return_value = "Use Docker"

        result = ask("How to deploy?", mock_index, mock_provider)

        assert result["answer"] == "Use Docker"
        assert result["sources"] == ["deploy.md"]
