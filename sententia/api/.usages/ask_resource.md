# AskResource — REST Question Resource

## Purpose

`AskResource` — REST adapter for the RAG pipeline (POST /ask).
Accepts an `AskRequest` with the query, delegates to `rag.ask()`, returns an `AskResponse` with the answer and sources.

## Usage

Instantiate with an `Index` and an LLM provider, then call `post()`:

```python
from sententia.api.ask import AskResource, AskRequest, AskResponse
from sententia.llm import OpenaiProvider

resource = AskResource(index=index, llm_provider=OpenaiProvider(url="...", model="llama3"))
response = resource.post(AskRequest(query="как настроить авторизацию?"))
print(response.answer)   # "Configure OAuth2..."
print(response.sources)  # ["auth.md"]

# Override default top
response = resource.post(AskRequest(query="как настроить авторизацию?", top=5))
```

## Constructor Parameters

- `index: Index` — search index instance
- `llm_provider: OpenaiProvider | AnthropicProvider` — LLM provider backend
- `top: int = 10` — default number of search results (applied when the request omits `top`)

## AskRequest Parameters

- `query: str` — question text (defaults to empty string)
- `top: int | None` — number of context chunks. Falls back to the constructor default when `None`

## Error Handling

Raises `HTTPException(502)` on `LLMProviderError`.