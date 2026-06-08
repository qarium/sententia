# Конфигурация приложения

SententiaConfig — модель конфигурации с поддержкой ENV переменных и env-файла.

## Создание

Базовое создание — загружает значения из ENV и .env файла:

    from sententia.config import SententiaConfig

    config = SententiaConfig()

С кастомным env-файлом:

    config = SententiaConfig(env_file="/path/to/.env")

## Перекрытие из CLI

Для передачи значений из CLI аргументов:

    config = SententiaConfig(
        env_file=result.env_file,
        cli_overrides={
            "data_dir": result.data_dir,
            "llm_protocol": result.llm_protocol,
            "llm_url": result.llm_url,
            "llm_model": result.llm_model,
            "mcp": result.mcp,
            "port": result.port,
        },
    )

Приоритет: cli_overrides > ENV > env-файл > дефолты.

## ENV переменные

| Переменная              | Поле         | Дефолт    |
|-------------------------|-------------|-----------|
| SENTENTIA_DATA_DIR      | data_dir    | ""        |
| SENTENTIA_INDEX_PATH    | index_path  | ""        |
| SENTENTIA_LLM_PROTOCOL  | llm_protocol| ""        |
| SENTENTIA_LLM_URL       | llm_url     | ""        |
| SENTENTIA_LLM_MODEL     | llm_model   | ""        |
| SENTENTIA_LLM_TOKEN     | llm_token   | ""        |
| SENTENTIA_MCP           | mcp         | False     |
| SENTENTIA_HOST          | host        | "0.0.0.0" |
| SENTENTIA_PORT          | port        | 8000      |