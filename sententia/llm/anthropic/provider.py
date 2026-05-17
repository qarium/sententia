from __future__ import annotations

import httpx

from ..provider import Provider
from ..provider.errors import LLMProviderError


class AnthropicProvider(Provider):
    def generate(self, prompt: str) -> str:
        if not self.token:
            raise LLMProviderError("Anthropic provider requires an API key (--llm-token)")

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "x-api-key": self.token,
            "anthropic-version": "2023-06-01",
        }

        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,
        }

        try:
            response = httpx.post(
                f"{self.url}/v1/messages",
                json=body,
                headers=headers,
                timeout=30.0,
            )
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Anthropic request failed: {exc}") from exc

        if not response.is_success:
            raise LLMProviderError(f"Anthropic API error: {response.status_code} {response.text}")

        try:
            return response.json()["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError(f"Unexpected Anthropic response format: {response.text}") from exc
