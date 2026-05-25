from __future__ import annotations

import httpx

from ..provider import Provider
from ..provider.errors import LLMProviderError


class OpenaiProvider(Provider):
    """LLM provider for OpenAI-compatible APIs (OpenAI, Ollama)."""

    def generate(self, prompt: str) -> str:
        """Generate text using OpenAI chat completions API.

        Args:
            prompt: Input text for generation.

        Returns:
            Generated text from the API response.

        Raises:
            LLMProviderError: On request failure or unexpected response format.
        """
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"

        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            response = httpx.post(
                f"{self.url}/v1/chat/completions",
                json=body,
                headers=headers,
                timeout=30.0,
            )
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"OpenAI request failed: {exc}") from exc

        if not response.is_success:
            raise LLMProviderError(f"OpenAI API error: {response.status_code} {response.text}")

        try:
            return response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError(f"Unexpected OpenAI response format: {response.text}") from exc
