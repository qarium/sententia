from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import HTTPException

from ...endpoints import RESTResource
from .models import FileResponse

if TYPE_CHECKING:
    from sententia.storage import Storage


class FilesResource(RESTResource):
    url_rule = "/files/{path:path}"

    def __init__(self, storage: Storage, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._storage = storage

    def get(self, path: str) -> FileResponse:
        try:
            content = self._storage.read_file(path)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except (FileNotFoundError, UnicodeDecodeError) as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return FileResponse(text=content["text"], source=content["source"])
