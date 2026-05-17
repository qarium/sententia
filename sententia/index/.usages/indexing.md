# Индексация Markdown-файлов

Создайте экземпляр `Index` со Storage и (опционально) путём к файлу индекса.

## Персистентный режим (с index_path)

  storage = Storage("/path/to/markdown/docs")
  index = Index(storage, "/path/to/index.faiss")
  # → индекс загружен из файла или создан и сохранён на диск

При создании индекс загружается из файла, если он существует.
Для переиндексации вызовите `index.index_directory()`:
  info = index.index_directory()
  # → {"files": 12, "chunks": 156, "dimensions": 768}

## In-memory режим (без index_path)

  storage = Storage("/path/to/markdown/docs")
  index = Index(storage)
  # → индекс создан из .md файлов, существует только в памяти

Индекс строится с нуля при каждом создании экземпляра.
Методы `save()` и `load()` недоступны — выбрасывают ошибку.