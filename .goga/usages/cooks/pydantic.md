# Pydantic v2 — Data Validation and Serialization

## BaseSettings — Environment Variable and Env File Loading

The `pydantic-settings` package provides `BaseSettings` for models that load configuration values from environment variables and `.env` files:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",          # prefix for ENV variables
        env_file=".env",            # path to env file
        env_file_encoding="utf-8",
        extra="ignore",             # ignore unrecognized variables
    )

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
```

The resolution order for configuration sources (highest priority first): constructor arguments > environment variables > env file > field defaults.

```python
# Environment: APP_HOST=127.0.0.1
config = AppConfig()
assert config.host == "127.0.0.1"

# Constructor argument takes precedence over environment variable
config = AppConfig(host="10.0.0.1")
assert config.host == "10.0.0.1"
```

To apply additional overrides beyond the standard resolution order, use a `model_validator` with `mode="before"` that merges a `cli_overrides` dict into the values:

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

## Models with kw_only and Default Values

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

Default value conventions for field types:
- `str` fields default to `""` (empty string)
- `int` fields default to `0`
- `float` fields default to `0.0`
- `list` fields use `Field(default_factory=list)` — never assign `[]` directly to avoid the mutable default trap

## Field Types

```python
class DataModel(BaseModel):
    model_config = ConfigDict(kw_only=True)

    name: str = ""
    count: int = 0
    score: float = 0.0
    tags: list = Field(default_factory=list)
```

## Serialization

The `BaseModel` class exposes four methods for serialization and deserialization:

```python
# -> dict
d = model.model_dump()

# -> JSON string
j = model.model_dump_json()

# <- dict
m = Model.model_validate({"field": "value"})

# <- JSON string
m = Model.model_validate_json('{"field": "value"}')
```