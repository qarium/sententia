# CLI аргументы

Парсинг CLI аргументов через parse_cli_args.

## Использование

    from sententia.cli import parse_cli_args

    result = parse_cli_args()           # из sys.argv
    result = parse_cli_args(["data"])   # из переданного списка

## Результат — ParseCliResult

Свойства:
- data_dir: str — путь к директории с Markdown-файлам
- env_file: str | None — путь к env-файлу
- index_path: str | None — путь к файлу FAISS индекса
- llm_protocol: str — тип LLM провайдера
- llm_url: str — URL API endpoint
- llm_model: str — идентификатор модели
- llm_token: str | None — API-ключ
- mcp: bool — флаг MCP Server
- host: str — адрес привязки
- port: int — порт сервера

## CLI аргументы

Позиционные:
  data_dir — путь к директории с Markdown-файлами

Опции:
  --env-file — путь к env-файлу конфигурации. Если не указан — используется ".env" по умолчанию.
  --index-path — путь к файлу FAISS индекса
  --llm-protocol — тип LLM (openai, anthropic, ollama). Обязателен.
  --llm-url — URL API endpoint. Обязателен.
  --llm-model — идентификатор модели. Обязателен.
  --llm-token — API-ключ
  --mcp — запустить как MCP Server
  --host — адрес привязки (по умолчанию 0.0.0.0)
  --port — порт сервера (по умолчанию 8000)