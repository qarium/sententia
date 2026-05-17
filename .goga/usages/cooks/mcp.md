# MCP Python SDK

## Назначение

Библиотека `mcp` — официальный Python SDK от Anthropic для реализации MCP (Model Context Protocol) серверов и клиентов.
Используется для предоставления инструментов (tools) внешним MCP-клиентам (Claude Desktop, Cursor и др.).

**Пакет:** `mcp>=1.27.0`

## Ключевые компоненты

### FastMCP

Высокоуровневый сервер для быстрого создания MCP Server.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="ServerName",
    instructions="Описание сервера для клиентов",
    json_response=True,       # JSON вместо SSE где возможно
    stateless_http=True,      # нет sticky sessions, проще деплой
)
```

### Определение инструментов (tools)

Инструменты регистрируются через `mcp.tool()`. Типы аннотаций функции автоматически формируют JSON Schema для клиентов.

#### Декоратор

```python
@mcp.tool()
def search(query: str, limit: int = 10) -> list[str]:
    """Поиск по базе знаний."""
    return ["result-1", "result-2"]

@mcp.tool()
async def ask(question: str) -> str:
    """Вопрос-ответ с RAG."""
    return "answer"
```

#### Программная регистрация существующего метода

`mcp.tool()` можно вызвать как функцию, передав callable напрямую (без использования как декоратора).
Это позволяет регистрировать bound-методы существующих объектов через wrapper-функцию:

```python
class MyTool:
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "Описание инструмента"

    def execute(self, query: str, top: int = 5) -> list[str]:
        return ["result"]

tool = MyTool()

# Создание wrapper-функции для регистрации в FastMCP
def _make_wrapper(t):
    def wrapper(query: str, top: int = 5) -> list[str]:
        return t.execute(query, top)
    wrapper.__name__ = t.name
    wrapper.__doc__ = t.description
    return wrapper

mcp.tool(_make_wrapper(tool))
```

Правила wrapper-функции:
- `__name__` — имя инструмента в MCP протоколе
- `__doc__` — описание инструмента (docstring становится description в MCP)
- Сигнатура с type annotations — FastMCP извлекает из неё JSON Schema для параметров
- Вызывает `tool.execute()` с соответствующими аргументами

#### Общие правила

- Docstring становится описанием инструмента в MCP протоколе
- Поддерживаются sync и async функции
- Возвращаемые типы: Pydantic модели, TypedDict, dataclasses, встроенные коллекции — автоматически сериализуются

### Standalone запуск (Streamable HTTP)

Streamable HTTP — рекомендуемый транспорт. Сервер запускается standalone через `mcp.run()`.

```python
mcp = FastMCP("ServerName", stateless_http=True, json_response=True)

# ... определение инструментов ...

# Запуск как standalone ASGI сервер
mcp.run(transport="streamable-http")
```

При вызове `mcp.run(transport="streamable-http")` запускается встроенный ASGI сервер (uvicorn). Настраиваемые параметры:

```python
mcp.settings.host = "127.0.0.1"  # хост
mcp.settings.port = 8000          # порт
```

## Конструктор FastMCP

| Параметр | По умолчанию | Описание |
|---|---|---|
| `name` | обязателен | Имя сервера в MCP протоколе |
| `instructions` | `None` | Человекочитаемое описание сервера |
| `host` | `"127.0.0.1"` | Хост для standalone запуска |
| `port` | `8000` | Порт для standalone запуска |
| `json_response` | `False` | JSON ответы вместо SSE |
| `stateless_http` | `False` | Stateless режим (нет sticky sessions) |
| `streamable_http_path` | `"/mcp"` | URL path для Streamable HTTP |