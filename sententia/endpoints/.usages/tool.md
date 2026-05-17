# MCPTool — базовый тип MCP инструмента

## Назначение

`MCPTool` — базовый тип для MCP инструментов. Определяет контракт для внешних MCP-клиентов. Мутируется конкретными реализациями (SearchTool, AskTool, FilesTool).

## Использование

Создайте подкласс `MCPTool`, реализовав свойства `name`, `description` и метод `execute`:

```python
class SearchTool(MCPTool):
    name = "search"
    description = "Search for relevant documents"

    def execute(self, query: str, top: int = 10) -> list[SearchToolResult]:
        # реализация
```

## Регистрация в MCP Server

Для регистрации инструмента в FastMCP создайте wrapper-функцию, которая делегирует вызов методу `execute`, и передайте её в декоратор `@mcp.tool()`:

```python
from mcp.server.fastmcp import FastMCP
import inspect

mcp = FastMCP("MyServer")

tool = MyTool()  # мутированный MCPTool

def wrapper(**kwargs):
    return tool.execute(**kwargs)

sig = inspect.signature(tool.execute)
params = dict(sig.parameters)
params.pop("self", None)
wrapper.__signature__ = sig.replace(parameters=list(params.values()))
wrapper.__name__ = tool.name
wrapper.__doc__ = tool.description

mcp.tool()(wrapper)
```

## Правила

- Базовая реализация `execute()` выбрасывает NotImplementedError
- Свойства `name` и `description` обязательны — имя и описание инструмента для MCP-клиентов
- Переопределяйте `execute()` с конкретной сигнатурой аргументов
- Паттерн мутации: конкретный инструмент наследует MCPTool, определяет name/description, переопределяет execute()
