from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import HTTPException

from ...endpoints import RESTResource
from ...llm.provider.errors import LLMProviderError
from ...rag import rag
from .models import AskRequest, AskResponse

if TYPE_CHECKING:
    from sententia.index import Index
    from sententia.llm.provider import Provider


class AskResource(RESTResource):
    """REST resource for RAG question answering over indexed documents."""

    url_rule = "/ask"

    def __init__(
        self,
        index: Index,
        llm_provider: Provider,
        top: int = 10,
        **kwargs: Any,
    ) -> None:
        """Initialize ask resource.

        Args:
            index: Index instance for semantic search.
            llm_provider: Provider instance for answer generation.
            top: Number of search results to include in context.
            **kwargs: Additional keyword arguments passed to RESTResource.
        """
        super().__init__(**kwargs)
        self._index = index
        self._llm_provider = llm_provider
        self._top = top

    def post(self, request: AskRequest) -> AskResponse:
        """Handle ask request and return generated answer with sources.

        Args:
            request: Ask request with user question.

        Returns:
            Ask response with generated answer and source references.
        """
        try:
            result = rag.ask(request.query, self._index, self._llm_provider, self._top)
        except LLMProviderError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        return AskResponse(answer=result["answer"], sources=result["sources"])
