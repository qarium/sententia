from __future__ import annotations

from pathlib import Path


class Storage:
    """Entity: manages file reading with path traversal protection.

    Args:
        directory_path: Absolute path to the root directory for file access.
    """

    def __init__(self, directory_path: str) -> None:
        self._base = Path(directory_path).resolve()

    def list_files(self) -> list[str]:
        """List all .md files recursively relative to the storage root.

        Returns:
            Sorted list of relative paths to .md files.
        """
        paths = self._base.rglob("*.md")
        return sorted(str(p.relative_to(self._base)) for p in paths)

    def read_file(self, file_path: str) -> dict[str, str]:
        """Read a .md file relative to the storage root.

        Args:
            file_path: Relative path of the file to read.

        Returns:
            dict with 'text' (file content) and 'source' (relative file path).

        Raises:
            ValueError: If path traversal is detected.
            FileNotFoundError: If the file does not exist or is not a .md file.
        """
        full_path = (self._base / file_path).resolve()

        if not full_path.is_relative_to(self._base):
            raise ValueError("Path traversal detected")
        if not full_path.is_file() or full_path.suffix.lower() != ".md":
            raise FileNotFoundError(f"File not found: {file_path}")

        text = full_path.read_text(encoding="utf-8")
        source = str(full_path.relative_to(self._base))

        return {"text": text, "source": source}
