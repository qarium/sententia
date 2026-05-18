# Indexing & Search

Markdown file indexing and semantic search powered by FAISS + Sentence-Transformers.

## Creation

=== "Persistent mode"
    ```python
    from sententia.storage import Storage
    from sententia.index import Index

    storage = Storage("/path/to/markdown/docs")
    index = Index(storage, "/path/to/index.faiss")
    ```
    On creation, the index is loaded from the file if it exists.

=== "In-memory mode"
    ```python
    from sententia.storage import Storage
    from sententia.index import Index

    storage = Storage("/path/to/markdown/docs")
    index = Index(storage)
    ```
    The index is built from scratch each time. `save()` and `load()` are unavailable.

## Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `storage` | `Storage` | — | File storage instance |
| `index_path` | `str \| None` | `None` | Path to index file. `None` for in-memory |
| `default_top` | `int` | `10` | Default number of search results |

## Indexing

```python
info = index.index_directory()
# {"files": 12, "chunks": 156, "dimensions": 768}
```

Algorithm:

1. Get file list and read content
2. Strip Markdown markup (code blocks, images, links, headings)
3. Split text into chunks with overlap
4. Add `"passage: "` prefix to each chunk (E5 model requirement)
5. Generate embeddings and normalize vectors
6. Create FAISS index (`IndexFlatIP`)

## Search

```python
results = index.search("how to set up authentication", top=5)
# [{"text": "...", "source": "docs/auth.md", "score": 0.95}, ...]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | — | Search query text (auto-prefixed with `"query: "`) |
| `top` | `int \| None` | `default_top` | Number of results |

Results are sorted by `score` descending (cosine similarity).

## Save & Load

```python
# Save index to disk (persistent mode only)
index.save()

# Load index from disk
loaded = index.load()  # True / False
```

!!! warning "In-memory mode"
    `save()` and `load()` raise an error when `index_path` is `None`.