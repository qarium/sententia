# FilesResource — REST ресурс файлов

## Назначение

`FilesResource` — REST ресурс для чтения содержимого файла. Адаптер GET /files/{path:path}.

## Использование

Создайте экземпляр с Storage, затем вызовите get():

```python
from sententia.storage import Storage
from sententia.api.files import FilesResource

storage = Storage(directory_path="/data/docs")
resource = FilesResource(storage=storage)
result = resource.get(path="docs/auth.md")
# result.text — содержимое файла
# result.source — относительный путь
```

## Обработка ошибок

- FileNotFoundError / UnicodeDecodeError → HTTP 404
- PermissionError → HTTP 403
- ValueError (path traversal) → HTTP 404