from typing import Any


class RESTResource:
    """Base class for REST resources. Defines HTTP handler contract."""

    @property
    def url_rule(self) -> str:
        raise NotImplementedError

    def get(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Method Not Allowed")

    def post(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Method Not Allowed")

    def put(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Method Not Allowed")

    def delete(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Method Not Allowed")
