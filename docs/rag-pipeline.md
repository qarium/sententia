# RAG Pipeline

Full pipeline: search for relevant chunks → build prompt → generate answer via LLM.

## Usage

```python
from sententia.llm.openai import OpenaiProvider
from sententia.index import Index
from sententia.storage import Storage
from sententia.rag import ask

storage = Storage("/data/markdown")
index = Index(storage, "/data/index.faiss")
provider = OpenaiProvider("https://api.openai.com", "gpt-4", "sk-...")
result = ask("how to set up authentication?", index, provider, top=10)
# {"answer": "To set up authentication...", "sources": ["docs/auth.md", "docs/setup.md"]}
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | — | User question text |
| `index` | `Index` | — | Index instance for chunk search |
| `llm_provider` | `Provider` | — | Configured LLM provider |
| `top` | `int` | `10` | Number of context chunks |

## Result

```python
{
    "answer": "Generated answer text",
    "sources": ["docs/auth.md", "docs/setup.md"]
}
```

- `answer` — generated answer text
- `sources` — list of unique source file paths (order preserved)

## Algorithm

1. Find relevant chunks via `index.search(query, top)`
2. Join chunk texts with double newline
3. Build prompt:
   - Opening: "Use the following context to answer the question:"
   - Context block: chunk texts wrapped in triple backticks
   - Question block: `query` wrapped in triple backticks
   - Instruction: if context is insufficient, respond "Insufficient data to answer this question"
4. Generate answer via `llm_provider.generate(prompt)`
5. Extract unique source file paths

## Insufficient Data

If the context is insufficient to answer, the LLM will return:

> "Insufficient data to answer this question"