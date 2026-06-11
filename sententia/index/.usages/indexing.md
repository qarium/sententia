# Indexing Markdown Files

Create an `Index` instance with a `Storage` instance and an optional index file path.

## Persistent Mode (with index_path)

  storage = Storage("/path/to/markdown/docs")
  index = Index(storage, "/path/to/index.faiss")
  # → index loaded from disk, or built and persisted on first run

On instantiation, the index is restored from disk if the file exists.
To force a full re-index, call `index.index_directory()`:
  info = index.index_directory()
  # → {"files": 12, "chunks": 156, "dimensions": 768}

## In-Memory Mode (without index_path)

  storage = Storage("/path/to/markdown/docs")
  index = Index(storage)
  # → index built from .md files, held entirely in memory

The index is reconstructed from scratch on every instantiation.
The `save()` and `load()` methods raise errors in this mode.
