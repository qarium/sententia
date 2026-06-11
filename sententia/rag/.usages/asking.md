# Answer Generation (RAG)

Invoke `ask(query, index, llm_provider, top)` to generate an answer to the user question
derived from indexed document chunks.

Example:
  from sententia.llm.openai import OpenaiProvider
  from sententia.index import Index
  from sententia.storage import Storage
  from sententia.rag import ask

  storage = Storage("/data/markdown")
  index = Index(storage, "/data/index.faiss")
  provider = OpenaiProvider("https://api.openai.com", "gpt-4", "sk-...")
  result = ask("how to configure authorization?", index, provider, top=10)
  # → {"answer": "To configure authorization...", "sources": ["docs/auth.md", "docs/setup.md"]}

The `ask` routine orchestrates the full pipeline: it retrieves relevant chunks via `index.search()`,
assembles a context-enriched prompt, and delegates generation to `llm_provider.generate()`.

When the context is insufficient, the response contains "Insufficient data to answer this question".
