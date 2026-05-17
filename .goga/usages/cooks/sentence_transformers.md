# Sentence-Transformers — генерация эмбеддингов

Модель: `intfloat/multilingual-e5-base`. Размерность: 768. Поддержка кириллицы и латиницы.

## Загрузка модели

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/multilingual-e5-base")
```

## Префиксы E5 (обязательно)

Без префиксов качество поиска значительно падает:
- Документы (индексация): `"passage: "` + текст
- Запросы (поиск): `"query: "` + текст

## Генерация эмбеддингов

```python
# Батч документов
texts = ["passage: " + chunk for chunk in chunks]
embeddings = model.encode(texts)
# numpy array, shape (n, 768), dtype float32

# Один запрос
query_vec = model.encode(["query: " + query])
# numpy array, shape (1, 768), dtype float32
```

Нормализация векторов выполняется через `np.linalg.norm` с явным присвоением результата перед добавлением в индекс и поиском.

## Формат результата

| Вызов                          | Тип           | Shape         |
|--------------------------------|---------------|---------------|
| `encode("текст")`              | numpy.ndarray | (768,) — 1D   |
| `encode(["текст1", "текст2"])` | numpy.ndarray | (2, 768) — 2D |
