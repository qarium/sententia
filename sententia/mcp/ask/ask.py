from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...endpoints import MCPTool
from ...llm.provider.errors import LLMProviderError
from ...rag import rag
from .models import AskToolResult

if TYPE_CHECKING:
    from sententia.index import Index
    from sententia.llm.provider import Provider


class AskTool(MCPTool):
    """MCP tool for RAG question answering over indexed documents."""

    name = "ask"
    description = "Ask a question and get an answer based on indexed documents"

    def __init__(
        self,
        index: Index,
        llm_provider: Provider,
        top: int = 10,
        **kwargs: Any,
    ) -> None:
        """Initialize ask tool.

        Args:
            index: Index instance for semantic search.
            llm_provider: Provider instance for answer generation.
            top: Number of search results to include in context.
            **kwargs: Additional keyword arguments passed to MCPTool.
        """
        super().__init__(**kwargs)
        self._index = index
        self._llm_provider = llm_provider
        self._top = top

    def execute(self, query: str) -> AskToolResult:
        """Execute RAG question answering and return answer with sources.

        Args:
            query: User question text.

        Returns:
            Ask result with generated answer and source references.
        """
        try:
            result = rag.ask(query, self._index, self._llm_provider, self._top)
        except LLMProviderError as exc:
            raise LLMProviderError(f"Failed to generate answer: {exc}") from exc

        return AskToolResult(answer=result["answer"], sources=result["sources"])
