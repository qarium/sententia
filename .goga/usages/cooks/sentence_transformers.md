# Sentence-Transformers — Embedding Generation

Model: `intfloat/multilingual-e5-base`. Dimensionality: 768. Supports Cyrillic and Latin scripts.

## Loading the Model

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/multilingual-e5-base")
```

## E5 Prefixes (mandatory)

The model requires input text prefixes. Without them, search quality drops significantly:
- Documents (indexing): `"passage: "` + text
- Queries (search): `"query: "` + text

## Generating Embeddings

```python
# Document batch
texts = ["passage: " + chunk for chunk in chunks]
embeddings = model.encode(texts)
# numpy array, shape (n, 768), dtype float32

# Single query
query_vec = model.encode(["query: " + query])
# numpy array, shape (1, 768), dtype float32
```

Normalize vectors using `np.linalg.norm` with explicit result assignment before adding to the index and performing search.

## Result Format

| Call                           | Type           | Shape         |
|--------------------------------|----------------|---------------|
| `encode("text")`               | numpy.ndarray  | (768,) — 1D   |
| `encode(["text1", "text2"])`   | numpy.ndarray  | (2, 768) — 2D |