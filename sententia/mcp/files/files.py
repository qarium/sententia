from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...endpoints import MCPTool
from .models import FilesToolResult

if TYPE_CHECKING:
    from sententia.storage import Storage


class FilesTool(MCPTool):
    name = "files"
    description = "Read file content by path"

    def __init__(self, storage: Storage, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._storage = storage

    def execute(self, path: str) -> FilesToolResult:
        try:
            content = self._storage.read_file(path)
        except PermissionError as exc:
            raise PermissionError(f"Access denied: {path}") from exc
        except (FileNotFoundError, ValueError, UnicodeDecodeError) as exc:
            raise FileNotFoundError(f"File not found: {path}") from exc
        return FilesToolResult(text=content["text"], source=content["source"])
