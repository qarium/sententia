from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...endpoints import MCPTool
from .models import FilesToolResult

if TYPE_CHECKING:
    from sententia.storage import Storage


class FilesTool(MCPTool):
    """MCP tool for reading markdown file content by path."""

    name = "files"
    description = "Read file content by path"

    def __init__(self, storage: Storage, **kwargs: Any) -> None:
        """Initialize files tool.

        Args:
            storage: Storage instance for file access.
            **kwargs: Additional keyword arguments passed to MCPTool.
        """
        super().__init__(**kwargs)

        self._storage = storage

    def execute(self, path: str) -> FilesToolResult:
        """Read and return file content by relative path.

        Args:
            path: Relative path to the markdown file.

        Returns:
            Files result with text content and source path.

        Raises:
            PermissionError: If access is denied.
            FileNotFoundError: If file is not found.
        """
        try:
            content = self._storage.read_file(path)
        except PermissionError as exc:
            raise PermissionError(f"Access denied: {path}") from exc
        except (FileNotFoundError, ValueError, UnicodeDecodeError) as exc:
            raise FileNotFoundError(f"File not found: {path}") from exc

        return FilesToolResult(text=content["text"], source=content["source"])
