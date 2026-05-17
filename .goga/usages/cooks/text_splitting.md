# Разбиение текста на фрагменты (chunking)

Размер чанка: ~500-800 символов. Overlap: ~10%.

## Кастомный Markdown-сплиттер

```python
import re

def split_text(text: str, chunk_size: int = 600, overlap: int = 60) -> list[str]:
    """Разбивает текст на фрагменты с перекрытием."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if end < len(text):
            # Обрезаем по последнее слово, не посреди
            last_space = chunk.rfind(" ")
            if last_space > chunk_size // 2:
                chunk = chunk[:last_space]
                end = start + last_space
        chunks.append(chunk.strip())
        start = end - overlap
    return chunks
```

## LangChain RecursiveCharacterTextSplitter (альтернатива)

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=60,
    separators=["\n\n", "\n", " ", ""],
)
chunks = splitter.split_text(text)
```
