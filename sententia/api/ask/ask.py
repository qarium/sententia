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
    url_rule = "/ask"

    def __init__(
        self,
        index: Index,
        llm_provider: Provider,
        top: int = 10,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._index = index
        self._llm_provider = llm_provider
        self._top = top

    def post(self, request: AskRequest) -> AskResponse:
        try:
            result = rag.ask(request.query, self._index, self._llm_provider, self._top)
        except LLMProviderError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return AskResponse(answer=result["answer"], sources=result["sources"])
