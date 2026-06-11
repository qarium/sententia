# FilesResource — REST File Resource

## Purpose

`FilesResource` — REST adapter for file content retrieval (GET /files/{path:path}).

## Usage

Instantiate with a `Storage`, then call `get()`:

```python
from sententia.storage import Storage
from sententia.api.files import FilesResource

storage = Storage(directory_path="/data/docs")
resource = FilesResource(storage=storage)
result = resource.get(path="docs/auth.md")
# result.text — file contents
# result.source — relative path
```

## Error Handling

- `FileNotFoundError` / `UnicodeDecodeError` → HTTP 404
- `PermissionError` → HTTP 403
- `ValueError` (path traversal) → HTTP 404