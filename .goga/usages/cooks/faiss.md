# FAISS — векторное хранилище

Размерность эмбеддингов: 768 (multilingual-e5-base). dtype: float32 обязательно.

## Создание индекса

IndexFlatIP — inner product. При L2-нормализации векторов inner product = cosine similarity.

```python
import faiss

index = faiss.IndexFlatIP(768)
```

## L2 нормализация (обязательна)

Нормализовать ОБА набора — корпусные векторы перед add и запросы перед search:

```python
import numpy as np

norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
norms[norms == 0] = 1.0  # избегаем деления на ноль
embeddings = embeddings / norms  # shape (n, 768), dtype float64 → привести к float32
embeddings = embeddings.astype('float32')
```

## Добавление векторов

```python
norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
norms[norms == 0] = 1.0
embeddings = (embeddings / norms).astype('float32')
index.add(embeddings)
# index.ntotal — количество добавленных векторов
```

## Поиск top-N

```python
q_norms = np.linalg.norm(query_vector, axis=1, keepdims=True)
q_norms[q_norms == 0] = 1.0
query_vector = (query_vector / q_norms).astype('float32')

distances, indices = index.search(query_vector, top)
# distances: shape (1, top) — cosine similarity [0..1]
# indices:   shape (1, top) — порядковые номера

results = []
for i in range(len(indices[0])):
    idx = int(indices[0][i])
    if idx < 0:          # FAISS возвращает -1 если результатов < top
        break
    results.append({
        "text": chunks[idx]["text"],
        "source": chunks[idx]["source"],
        "score": float(distances[0][i]),
    })
```

## Сохранение и загрузка

FAISS сохраняет только векторы. Метаданные (chunks) сохраняются отдельно:

```python
# Сохранение индекса
faiss.write_index(index, "index.faiss")

# Загрузка индекса
index = faiss.read_index("index.faiss")

# Метаданные — отдельно через json/pickle
import json
with open("index.faiss.metadata", "w") as f:
    json.dump({"chunks": chunks}, f, ensure_ascii=False)
```
