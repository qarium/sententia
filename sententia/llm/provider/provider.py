from __future__ import annotations


class Provider:
    def __init__(self, url: str, model: str, token: str | None = None) -> None:
        self._url = url.rstrip("/")
        self._model = model
        self._token = token

    @property
    def url(self) -> str:
        return self._url

    @property
    def model(self) -> str:
        return self._model

    @property
    def token(self) -> str | None:
        return self._token

    def generate(self, prompt: str) -> str:
        raise NotImplementedError
