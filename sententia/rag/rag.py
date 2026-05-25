from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sententia.index import Index
    from sententia.llm.provider import Provider


def ask(query: str, index: Index, llm_provider: Provider, top: int = 10) -> dict:
    """RAG pipeline: search -> prompt -> generate -> return answer with sources.

    Args:
        query: User question.
        index: Index instance for semantic search.
        llm_provider: Provider instance for answer generation.
        top: Number of search results to include.

    Returns:
        dict with 'answer' (str) and 'sources' (list of unique source paths).
    """
    results = index.search(query, top)

    context = "\n\n".join(r["text"] for r in results)
    sources = list(dict.fromkeys(r["source"] for r in results))

    prompt = (
        f"Используй следующий контекст, чтобы ответить на вопрос:\n"
        f"```\n{context}\n```\n\n"
        f"Вопрос:\n```\n{query}\n```\n"
        f"\n\nЕсли предоставленный контекст недостаточен для ответа на вопрос — "
        f'ответь "Недостаточно данных для ответа на данный вопрос".'
    )

    answer = llm_provider.generate(prompt)

    return {"answer": answer, "sources": sources}
