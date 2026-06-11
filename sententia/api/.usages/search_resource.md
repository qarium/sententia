# SearchResource — REST Search Resource

## Purpose

`SearchResource` — REST adapter for semantic document search (POST /search).
Accepts a `SearchRequest` with the query, delegates to `index.search()`, returns a `SearchResponse` with ranked results.

## Usage

Instantiate with an `Index`, then call `post()`:

```python
from sententia.api.search import SearchResource, SearchRequest, SearchResponse

resource = SearchResource(index=index)
response = resource.post(SearchRequest(query="как настроить авторизацию?", top=10))
for item in response.results:
    print(item.source, item.score, item.text[:80])
```

## Constructor Parameters

- `index: Index` — search index instance

## Request Models

`SearchRequest`:
- `query: str` — search query string (defaults to `""`)
- `top: int` — number of results, range 1–100 (defaults to `10`)

## Response Models

`SearchResponse`:
- `results: list[SearchResultItem]` — list of search results

`SearchResultItem`:
- `text: str` — matched fragment text
- `source: str` — source file path
- `score: float` — relevance score