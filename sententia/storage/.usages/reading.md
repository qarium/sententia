# Reading Files

Create an instance of `Storage(directory_path)`.

## File Listing

  files = storage.list_files()
  # → ["docs/auth.md", "docs/setup.md", "guide.md"]

Returns a list of relative paths for all `.md` files within the directory.

## Reading a File

  content = storage.read_file("docs/auth.md")
  # → {"text": "# Authorization\n...", "source": "docs/auth.md"}

Raises `FileNotFoundError` if the file does not exist.
The `file_path` argument must be a relative path within `directory_path`; path traversal outside the root directory boundary is prohibited.
