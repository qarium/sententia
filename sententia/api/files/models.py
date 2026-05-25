from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class FileResponse(BaseModel):
    """Response body with file content and source path."""

    model_config = ConfigDict(kw_only=True)

    text: str = ""
    source: str = ""
