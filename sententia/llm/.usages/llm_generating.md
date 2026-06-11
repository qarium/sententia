# Basic LLM Provider Usage Pattern

All providers implement the unified interface generate(prompt: str) -> str.

Usage:
  answer = llm_provider.generate("Your prompt")
