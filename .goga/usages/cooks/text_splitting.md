# Text Chunking

Chunk size: ~500-800 characters. Overlap: ~10%.

## Custom Markdown Splitter

```python
import re

def split_text(text: str, chunk_size: int = 600, overlap: int = 60) -> list[str]:
    """Splits text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if end < len(text):
            # Trim at the last word boundary, not mid-word
            last_space = chunk.rfind(" ")
            if last_space > chunk_size // 2:
                chunk = chunk[:last_space]
                end = start + last_space
        chunks.append(chunk.strip())
        start = end - overlap
    return chunks
```

## LangChain RecursiveCharacterTextSplitter (alternative)

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=60,
    separators=["\n\n", "\n", " ", ""],
)
chunks = splitter.split_text(text)
```