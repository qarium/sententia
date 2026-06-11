# Semantic Search

Call `index.search(query, top)` to search for relevant fragments.
The query automatically receives the prefix "query: " for the E5 model.
The index is an `Index` instance from the `sententia/index` cell.

Example:
  results = index.search("how to set up authorization", top=5)
  # → [{"text": "...", "source": "docs/auth.md", "score": 0.95}, ...]

Results are sorted by score in descending order (cosine similarity).
If top is not specified, default_top is used (defaults to 10).