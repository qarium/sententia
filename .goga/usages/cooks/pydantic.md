# Pydantic v2 — валидация данных и сериализация

## BaseSettings — загрузка из ENV и env-файла

Для моделей, загружающих значения из переменных окружения и env-файлов, используется `pydantic-settings`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",          # префикс ENV переменных
        env_file=".env",            # путь к env-файлу
        env_file_encoding="utf-8",
        extra="ignore",             # игнорировать лишние переменные
    )

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
```

Приоритет источников (от высокого к низкому): аргументы конструктора > ENV переменные > env-файл > дефолты.

```python
# Из ENV: APP_HOST=127.0.0.1
config = AppConfig()
assert config.host == "127.0.0.1"

# Аргумент конструктора перекрывает ENV
config = AppConfig(host="10.0.0.1")
assert config.host == "10.0.0.1"
```

Дополнительные перекрытия через kwargs реализуются через `model_validator`:

```python
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
    )

    host: str = "0.0.0.0"
    port: int = 8000

    @model_validator(mode="before")
    @classmethod
    def apply_overrides(cls, values: dict) -> dict:
        overrides = values.pop("cli_overrides", None) or {}
        values.update(overrides)
        return values
```

```python
config = AppConfig(cli_overrides={"host": "192.168.1.1"})
assert config.host == "192.168.1.1"
```

---

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
