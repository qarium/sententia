# Pydantic v2 — валидация данных и сериализация

## Модель с kw_only и дефолтами

```python
from pydantic import BaseModel, ConfigDict, Field

class SearchRequest(BaseModel):
    model_config = ConfigDict(kw_only=True)

    query: str = ""
    top: int = 5

class SearchResponse(BaseModel):
    model_config = ConfigDict(kw_only=True)

    results: list = Field(default_factory=list)
```

Правила дефолтов:
- str → `""` (пустая строка)
- int → `0`
- float → `0.0`
- list → `Field(default_factory=list)` (не `[]` напрямую — mutable default)

## Типы полей

```python
class DataModel(BaseModel):
    model_config = ConfigDict(kw_only=True)

    name: str = ""
    count: int = 0
    score: float = 0.0
    tags: list = Field(default_factory=list)
```

## Сериализация

```python
# -> dict
d = model.model_dump()

# -> JSON строка
j = model.model_dump_json()

# <- dict
m = Model.model_validate({"field": "value"})

# <- JSON строка
m = Model.model_validate_json('{"field": "value"}')
```
