# Storage

File storage — access to Markdown files from an indexed directory.

## Creation

```python
from sententia.storage import Storage

storage = Storage("/path/to/markdown/docs")
```

The constructor takes an absolute path to the root directory with Markdown files.

## List Files

```python
files = storage.list_files()
# ["docs/auth.md", "docs/setup.md", "guide.md"]
```

Recursively traverses the directory. Returns a list of relative paths for all `.md` files.

## Read File

```python
content = storage.read_file("docs/auth.md")
# {"text": "# Authentication\n...", "source": "docs/auth.md"}
```

| Behavior | Description |
|----------|-------------|
| Success | Returns `{"text": str, "source": str}` |
| File not found | `FileNotFoundError` |
| Path traversal | Protection against escaping the root directory |

## Usage with Index

Storage is passed to Index on creation:

```python
storage = Storage("/data/markdown")
index = Index(storage, "/data/index.faiss")
```