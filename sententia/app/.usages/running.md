# Запуск приложения

SententiaApp — контейнер без доменных зависимостей. Сборка компонентов выполняется в корневой ячейке (main).
Режимы работы взаимоисключающие: либо REST ресурсы (FastAPI), либо MCP tools (MCP Server).

## Регистрация REST ресурсов

Каждый ресурс предоставляет url_rule через своё свойство.
Для регистрации передайте ресурс в add_rest_resource:

  app = SententiaApp()
  app.add_rest_resource(resource)

## Регистрация MCP tools

Для регистрации передайте tool в add_mcp_tool:

  app = SententiaApp()
  app.add_mcp_tool(tool)

## Запуск сервера

Режим определяется зарегистрированными обработчиками:
- tools → MCP Server (Streamable HTTP)
- resources → FastAPI (uvicorn)

  app.run(host="0.0.0.0", port=8000)
