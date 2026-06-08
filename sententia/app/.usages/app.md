# Параметры приложения

Параметры приложения можно передать через аргументы командной строки (через main routine) или через ENV переменные.

Конфигурация инкапсулирована в SententiaConfig из sententia/config клетки:

    from sententia.config import SententiaConfig

    config = SententiaConfig(env_file=result.env_file, cli_overrides={...})

Приоритет: cli_overrides > ENV > env-файл > дефолты.

Обязательные параметры:
  data_dir — путь к директории с Markdown-файлам
  llm_protocol — тип LLM ("openai", "anthropic", "ollama")
  llm_url — URL API endpoint
  llm_model — идентификатор модели

Опциональные параметры:
  index_path — путь к файлу индекса. Если не указан — индекс строится в памяти без сохранения на диск
  llm_token — API-ключ (не нужен для Ollama)
  mcp — флаг режима MCP Server (по умолчанию False). При True запускается MCP Server вместо REST API
  host — адрес привязки (по умолчанию 0.0.0.0)
  port — порт сервера (по умолчанию 8000)
