from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import HTTPException

from ...endpoints import RESTResource
from .models import FileResponse

if TYPE_CHECKING:
    from sententia.storage import Storage


class FilesResource(RESTResource):
    """REST resource for reading markdown files by path."""

    url_rule = "/files/{path:path}"

    def __init__(self, storage: Storage, **kwargs: Any) -> None:
        """Initialize files resource.

        Args:
            storage: Storage instance for file access.
            **kwargs: Additional keyword arguments passed to RESTResource.
        """
        super().__init__(**kwargs)

        self._storage = storage

    def get(self, path: str) -> FileResponse:
        """Read and return file content by relative path.

        Args:
            path: Relative path to the markdown file.

        Returns:
            File response with text content and source path.

        Raises:
            HTTPException: 403 on access denied, 404 on file not found.
        """
        try:
            content = self._storage.read_file(path)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except (FileNotFoundError, UnicodeDecodeError) as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        return FileResponse(text=content["text"], source=content["source"])
