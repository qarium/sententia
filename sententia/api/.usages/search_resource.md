# SearchResource — REST ресурс поиска

## Назначение

`SearchResource` — REST адаптер для семантического поиска документов (POST /search).
Принимает SearchRequest с запросом, вызывает `index.search()`, возвращает SearchResponse с результатами.

## Использование

Создайте экземпляр с Index, затем вызовите post():

```python
from sententia.api.search import SearchResource, SearchRequest, SearchResponse

resource = SearchResource(index=index)
response = resource.post(SearchRequest(query="как настроить авторизацию?", top=10))
for item in response.results:
    print(item.source, item.score, item.text[:80])
```

## Параметры конструктора

- `index: Index` — экземпляр индекса для поиска

## Модели запроса

`SearchRequest`:
- `query: str` — поисковый запрос (по умолчанию `""`)
- `top: int` — количество результатов, от 1 до 100 (по умолчанию `10`)

## Модели ответа

`SearchResponse`:
- `results: list[SearchResultItem]` — список результатов поиска

`SearchResultItem`:
- `text: str` — текст найденного фрагмента
- `source: str` — источник (путь к файлу)
- `score: float` — релевантность результата