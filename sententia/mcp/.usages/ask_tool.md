# AskTool — MCP Question-Answer Tool

## Purpose

`AskTool` is an MCP tool that answers user questions using a RAG pipeline. It combines document retrieval via `Index` with answer generation via an LLM provider.

## Usage

Instantiate with an `Index` and an `llm_provider`, then invoke `execute()`:

```python
from sententia.mcp.ask import AskTool

tool = AskTool(index, llm_provider, top=10)
result = tool.execute(query="how to configure authorization?")
# → AskToolResult(answer="To configure...", sources=["docs/auth.md", "docs/setup.md"])

# Override default top-k retrieval count
result = tool.execute(query="how to configure authorization?", top=5)
```

## Error Handling

If the LLM provider raises `LLMProviderError`, `AskTool` propagates it as a tool error exception.
