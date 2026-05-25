from __future__ import annotations


class Provider:
    """Base class for LLM providers."""

    def __init__(self, url: str, model: str, token: str | None = None) -> None:
        """Initialize LLM provider.

        Args:
            url: API base URL.
            model: Model identifier.
            token: Optional API key for authentication.
        """
        self._url = url.rstrip("/")
        self._model = model
        self._token = token

    @property
    def url(self) -> str:
        """API base URL."""
        return self._url

    @property
    def model(self) -> str:
        """Model identifier."""
        return self._model

    @property
    def token(self) -> str | None:
        """API authentication key."""
        return self._token

    def generate(self, prompt: str) -> str:
        """Generate text from the given prompt.

        Args:
            prompt: Input text for generation.

        Returns:
            Generated text response.

        Raises:
            NotImplementedError: Subclass must implement this method.
        """
        raise NotImplementedError
