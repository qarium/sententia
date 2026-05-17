from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class FilesToolResult(BaseModel):
    model_config = ConfigDict(kw_only=True)

    text: str = ""
    source: str = ""
