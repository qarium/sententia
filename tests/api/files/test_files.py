from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sententia.api.files import FileResponse, FilesResource
from sententia.endpoints import RESTResource


class TestFilesContract:
    def test_file_response_importable(self):
        assert FileResponse is not None

    def test_files_resource_importable(self):
        assert FilesResource is not None

    def test_files_resource_is_restresource_subclass(self):
        assert issubclass(FilesResource, RESTResource)

    def test_files_resource_url_rule(self):
        mock_storage = MagicMock()
        resource = FilesResource(storage=mock_storage)
        assert resource.url_rule == "/files/{path:path}"


class TestFilesResourceLogic:
    def test_files_resource_get_returns_content(self):
        mock_storage = MagicMock()
        mock_storage.read_file.return_value = {
            "text": "# Auth",
            "source": "auth.md",
        }
        resource = FilesResource(storage=mock_storage)
        response = resource.get("auth.md")

        assert isinstance(response, FileResponse)
        assert response.text == "# Auth"
        assert response.source == "auth.md"

    def test_files_resource_get_not_found_returns_404(self):
        mock_storage = MagicMock()
        mock_storage.read_file.side_effect = FileNotFoundError("not found")
        resource = FilesResource(storage=mock_storage)

        with pytest.raises(HTTPException) as exc_info:
            resource.get("missing.md")
        assert exc_info.value.status_code == 404

    def test_files_resource_get_permission_denied_returns_403(self):
        mock_storage = MagicMock()
        mock_storage.read_file.side_effect = PermissionError("denied")
        resource = FilesResource(storage=mock_storage)

        with pytest.raises(HTTPException) as exc_info:
            resource.get("secret.md")
        assert exc_info.value.status_code == 403

    def test_files_resource_get_path_traversal_returns_404(self):
        mock_storage = MagicMock()
        mock_storage.read_file.side_effect = ValueError("Path traversal detected")
        resource = FilesResource(storage=mock_storage)

        with pytest.raises(HTTPException) as exc_info:
            resource.get("../../etc/passwd")
        assert exc_info.value.status_code == 404

    def test_files_resource_get_unicode_error_returns_404(self):
        mock_storage = MagicMock()
        mock_storage.read_file.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")
        resource = FilesResource(storage=mock_storage)

        with pytest.raises(HTTPException) as exc_info:
            resource.get("binary.bin")
        assert exc_info.value.status_code == 404
