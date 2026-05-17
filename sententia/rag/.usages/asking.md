# Генерация ответов (RAG)

Вызовите `ask(query, index, llm_provider, top)` для получения ответа на вопрос
на основе проиндексированных документов.

Пример:
  from sententia.llm.openai import OpenaiProvider
  from sententia.index import Index
  from sententia.storage import Storage
  from sententia.rag import ask

  storage = Storage("/data/markdown")
  index = Index(storage, "/data/index.faiss")
  provider = OpenaiProvider("https://api.openai.com", "gpt-4", "sk-...")
  result = ask("как настроить авторизацию?", index, provider, top=10)
  # → {"answer": "Для настройки авторизации...", "sources": ["docs/auth.md", "docs/setup.md"]}

Функция автоматически выполнит поиск релевантных чанков через index.search(),
соберёт промпт с контекстом и отправит в LLM через llm_provider.generate().

Если контекст недостаточен — ответ будет содержать "Недостаточно данных для ответа на данный вопрос".
