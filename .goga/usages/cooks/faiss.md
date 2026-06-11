# FAISS — Vector Store

Embedding dimension: 768 (multilingual-e5-base). dtype: float32 mandatory.

## Index Creation

`IndexFlatIP` computes inner product. When vectors are L2-normalized, inner product equals cosine similarity.

```python
import faiss

index = faiss.IndexFlatIP(768)
```

## L2 Normalization (Mandatory)

Normalize **both** sets — corpus vectors before `index.add()` and queries before `index.search()`:

```python
import numpy as np

norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
norms[norms == 0] = 1.0  # guard against division by zero
embeddings = embeddings / norms  # shape (n, 768), dtype float64 → cast to float32
embeddings = embeddings.astype('float32')
```

## Adding Vectors

```python
norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
norms[norms == 0] = 1.0
embeddings = (embeddings / norms).astype('float32')
index.add(embeddings)
# index.ntotal — number of added vectors
```

## Top-N Search

```python
q_norms = np.linalg.norm(query_vector, axis=1, keepdims=True)
q_norms[q_norms == 0] = 1.0
query_vector = (query_vector / q_norms).astype('float32')

distances, indices = index.search(query_vector, top)
# distances: shape (1, top) — cosine similarity [0..1]
# indices:   shape (1, top) — positional indices

results = []
for i in range(len(indices[0])):
    idx = int(indices[0][i])
    if idx < 0:          # FAISS returns -1 if results < top
        break
    results.append({
        "text": chunks[idx]["text"],
        "source": chunks[idx]["source"],
        "score": float(distances[0][i]),
    })
```

## Saving and Loading

FAISS stores only vectors. Metadata (chunks) are saved separately:

```python
# Save index
faiss.write_index(index, "index.faiss")

# Load index
index = faiss.read_index("index.faiss")

# Metadata — separately via json/pickle
import json
with open("index.faiss.metadata", "w") as f:
    json.dump({"chunks": chunks}, f, ensure_ascii=False)
```