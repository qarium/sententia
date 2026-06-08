# План: `add-config`

## Цель

Реализовать конфигурацию приложения через三层 систему приоритетов (CLI > ENV > env-файл > дефолты) и вынести парсинг CLI в отдельные ячейки `sententia/cli` и `sententia/config`. Переработать `main()` для делегирования в новые сущности. Покрыть контрактными, логическими и интеграционными тестами.

## Контекст

### Поверхность контракта

**Сущность: `ParseCliResult()`**
- Тип: class (Entity)
- Объявленный `location`: `cli.py` (в `sententia/cli/`)
- Обязанность фасада: должна быть импортируема из `sententia.cli`
- Свойства:
  - `data_dir -> str` — путь к директории с Markdown-файлами
  - `env_file -> str | None` — путь к env-файлу. None — использовать по умолчанию
  - `index_path -> str | None` — путь к файлу FAISS индекса. None — индекс в памяти
  - `llm_protocol -> str` — тип LLM провайдера: "openai", "anthropic", "ollama"
  - `llm_url -> str` — URL API endpoint LLM провайдера
  - `llm_model -> str` — идентификатор модели LLM
  - `llm_token -> str | None` — API-ключ. None — получить из ENV или env-файла
  - `mcp -> bool` — флаг режима MCP Server. По умолчанию False
  - `host -> str` — адрес привязки сервера. По умолчанию "0.0.0.0"
  - `port -> int` — порт сервера. По умолчанию 8000
- Семантические требования: Immutable data holder для результата CLI парсинга
- Импортированные зависимости: нет
- Контекст аннотаций: Использовать `conventions` для правил написания кода и тестов

**Сущность: `parse_cli_args(argv: list[str] | None = None) -> result:ParseCliResult`**
- Тип: function (Routine)
- Объявленный `location`: `cli.py` (в `sententia/cli/`)
- Обязанность фасада: должна быть импортируема из `sententia.cli`
- Семантические требования:
  - Парсинг CLI аргументов через argparse
  - Позиционный аргумент data_dir
  - Обязательные опции: --llm-protocol (choices), --llm-url, --llm-model
  - Опциональные: --env-file, --index-path, --llm-token, --mcp (flag), --host, --port
  - argv=None → использовать sys.argv
  - prog="sententia"
- Импортированные зависимости: нет
- Контекст аннотаций: Использовать `conventions` для правил написания кода и тестов

**Сущность: `SententiaConfig(env_file: str | None = None, cli_overrides: dict[str, Any] | None = None)`**
- Тип: class (Entity)
- Объявленный `location`: `config.py` (в `sententia/config/`)
- Обязанность фасада: должна быть импортируема из `sententia.config`
- Свойства:
  - `data_dir -> str` — путь к директории с Markdown-файлами
  - `index_path -> str | None` — путь к файлу FAISS индекса. None — индекс в памяти
  - `llm_protocol -> str` — тип LLM провайдера
  - `llm_url -> str` — URL API endpoint LLM провайдера
  - `llm_model -> str` — идентификатор модели LLM
  - `llm_token -> str | None` — API-ключ. None — токен не нужен (Ollama)
  - `mcp -> bool` — флаг режима MCP Server. По умолчанию False
  - `host -> str` — адрес привязки сервера. По умолчанию "0.0.0.0"
  - `port -> int` — порт сервера. По умолчанию 8000
- Семантические требования:
  - Загружает значения из ENV с префиксом SENTENTIA_ и из env-файла
  - Приоритет: cli_overrides > ENV > env-файл > дефолты
  - env_file=None → используется ".env" по умолчанию
  - cli_overrides=None → нет перекрытий, только ENV + env-file
- Импортированные зависимости: нет (внутренне использует pydantic-settings)
- Контекст аннотаций: Использовать `pydantic` для работы с моделью. Использовать `conventions` для правил написания кода и тестов

**Сущность: `main(argv: list[str] | None = None) -> void:None`**
- Тип: function (Routine)
- Объявленный `location`: `__main__.py` (в `sententia/`)
- Обязанность фасада: вызывается как `python -m sententia`
- Семантические требования:
  - Точка входа и сборки приложения
  - Координирует: parse_cli_args → SententiaConfig → Storage → Index → LLM Provider → Resources/Tools → SententiaApp.run
  - Матчинг протокола: openai/ollama → OpenaiProvider, anthropic → AnthropicProvider, else → ValueError
  - Режим mcp=True: MCP tools + MCP Server; mcp=False: REST resources + FastAPI
  - AskResource/AskTool передаётся top=10
- Импортированные зависимости: `ParseCliResult`, `parse_cli_args` из sententia/cli; `SententiaConfig` из sententia/config
- Контекст аннотаций: Использовать `configuration` для создания конфигурации. Использовать `cli` для парсинга CLI. Использовать `running` для запуска приложения.

### Реэкспорты

Нет реэкспортов в CODEMANIFEST ячеек cli и config.

### Контекст Usages

- **`conventions`** (`sententia/cli` и `sententia/config`): правила написания кода, тестов, форматирования. Python 3.10+, pydantic, pytest, ruff, kw_only=True, Google-style docstrings
- **`pydantic`** (`sententia/config`): паттерны работы с Pydantic v2 — BaseModel, ConfigDict, Field, сериализация. BaseSettings для ENV/env-file. model_validator для cli_overrides

### Импортированные Usages

- **`cli`** из `sententia/cli`: инструкция по парсингу CLI аргументов. Путь: `sententia/cli/.usages/cli.md`
- **`configuration`** из `sententia/config`: инструкция по созданию SententiaConfig. Путь: `sententia/config/.usages/configuration.md`
- **`app`** из `sententia/app`: параметры приложения через SententiaConfig. Путь: `sententia/app/.usages/app.md`
- **`running`** из `sententia/app`: запуск приложения и регистрация resources/tools. Путь: `sententia/app/.usages/running.md`

### Внешние зависимости

- `pydantic` (Pydantic v2) — BaseModel, ConfigDict, Field
- `pydantic-settings` — BaseSettings, SettingsConfigDict
- `argparse` (stdlib) — CLI парсинг
- `pytest` — тестирование
- `ruff` — линтинг

## Факты

- Ячейки `sententia/cli` и `sententia/config` не содержат кода — только CODEMANIFEST и `.usages/`
- Существующий `__main__.py` содержит `build_parser()` и `main()` — оба будут переработаны
- `build_parser()` удаляется, логика парсинга переходит в `sententia/cli/cli.py`
- `main()` переписывается для делегирования в `parse_cli_args` и `SententiaConfig`
- Существующие тесты в `tests/test_main.py` импортируют `build_parser` — потребуется обновление
- Фасад sententia root `__init__.py` не нуждается в изменении (не реэкспортирует cli/config)
- `ParseCliResult` может быть Pydantic BaseModel или dataclass — cookbook допускает оба варианта
- `None` значения из `ParseCliResult` (`env_file`, `index_path`, `llm_token`) передаются как `None` без преобразования

## Анализ разрывов

- **Отсутствующие сущности**: `ParseCliResult`, `parse_cli_args` (cli.py), `SententiaConfig` (config.py) — не реализованы
- **Отсутствующие фасады**: `sententia/cli/__init__.py` и `sententia/config/__init__.py` — не существуют
- **Несоответствия API**: `main()` не принимает `argv`, не делегирует в `parse_cli_args`/`SententiaConfig`
- **Существующий код для переиспользования**: `build_parser()` — основа для `parse_cli_args()`, логика main — основа для обновлённого `main()`
- **Разрывы в тестовом покрытии**: нет тестов для cli/config ячеек, существующие тесты main нужно переписать
- **Отсутствующие директории тестов**: `tests/cli/`, `tests/config/` — не существуют

---

## Tasks

### Task 1: Инфраструктура sententia/cli (инфраструктура)

Создать структуру ячейки `sententia/cli`: фасад `__init__.py` с реэкспортом `ParseCliResult` и `parse_cli_args`. Файл реализации `cli.py` с заглушками для `ParseCliResult` и `parse_cli_args`.

**КРИТИЧЕСКИ: файлы `CODEMANIFEST` — определения контракта только для чтения. НЕ изменяйте их. Если реализация не соответствует контракту, исправляйте реализацию — никогда не исправляйте контракт.**

- [x] Создать файл `sententia/cli/__init__.py` с `__all__`, содержащим `ParseCliResult` и `parse_cli_args`
- [x] Создать файл `sententia/cli/cli.py` с заглушками классов/функций (pass/NotImplementedError)
- [x] Проверить доступность фасада: `python -c "from sententia.cli import ParseCliResult, parse_cli_args"`
- [x] Линт: `ruff check sententia/cli/` — исправить форматирование при необходимости

### Task 2: Реализация ParseCliResult и parse_cli_args (TDD)

Реализовать `ParseCliResult` (data model) и `parse_cli_args` (argparse Routine) в `sententia/cli/cli.py`.

Сущности контракта:
- `ParseCliResult()` — Entity с 10 свойствами, все с дефолтами (кроме обязательных data_dir, llm_protocol, llm_url, llm_model)
- `parse_cli_args(argv: list[str] | None = None) -> result:ParseCliResult` — Routine для парсинга CLI

Алгоритм `parse_cli_args`:
1. IF argv is None: argv = sys.argv[1:]
2. ArgumentParser(prog="sententia") с позиционным data_dir и 8 опциями
3. args = parser.parse_args(argv)
4. RETURN ParseCliResult(data_dir=..., env_file=..., index_path=..., llm_protocol=..., llm_url=..., llm_model=..., llm_token=..., mcp=..., host=..., port=...)

Аннотации сущностей из CODEMANIFEST (sententia/cli):

**ParseCliResult**: Модель данных результата парсинга CLI аргументов. Содержит все распарсенные значения и путь к env-файлу. Использовать `conventions` для правил написания кода и тестов.

**parse_cli_args**: Парсинг CLI аргументов. `argv`: список аргументов. None — использовать sys.argv. Позиционные: data_dir — путь к директории с Markdown-файлами. Опции: --env-file — путь к env-файлу конфигурации, --index-path — путь к файлу FAISS индекса, --llm-protocol — тип LLM провайдера (openai, anthropic, ollama). Обязателен, --llm-url — URL API endpoint LLM. Обязателен, --llm-model — идентификатор модели. Обязателен, --llm-token — API-ключ, --mcp — флаг запуска в режиме MCP Server, --host — адрес привязки сервера, --port — порт сервера. Использовать `conventions` для правил написания кода и тестов.

**Usages, релевантные для этой задачи:**
- `conventions`: Python 3.10+, kw_only=True для моделей, Google-style docstrings, pytest для тестов

**КРИТИЧЕСКИ: файлы `CODEMANIFEST` — определения контракта только для чтения. НЕ изменяйте их. Если реализация не соответствует контракту, исправляйте реализацию — никогда не исправляйте контракт.**

- [x] **ШАГ 0**: Объявить работу над Task 2 — реализация ParseCliResult и parse_cli_args
- [x] **Контрактные тесты**: создать `tests/cli/__init__.py` и `tests/cli/test_cli.py`. Проверить: (1) `ParseCliResult` импортируем из `sententia.cli`, (2) `parse_cli_args` импортируем из `sententia.cli`, (3) сигнатура `parse_cli_args(argv=None)`, (4) `ParseCliResult` имеет 10 свойств с правильными типами (data_dir: str, env_file: str|None, index_path: str|None, llm_protocol: str, llm_url: str, llm_model: str, llm_token: str|None, mcp: bool, host: str, port: int)
- [x] **Код**: реализовать `ParseCliResult` как dataclass или Pydantic BaseModel с kw_only=True и 10 свойствами
- [x] **Код**: реализовать `parse_cli_args` через argparse с позиционным data_dir и 8 опциями (--env-file, --index-path, --llm-protocol required choices=["openai","anthropic","ollama"], --llm-url required, --llm-model required, --llm-token, --mcp store_true, --host default="0.0.0.0", --port type=int default=8000)
- [x] **Код**: обновить фасад `sententia/cli/__init__.py` — реэкспортировать `ParseCliResult` и `parse_cli_args`
- [x] **Верификация интерфейсов**: запустить контрактные тесты — `pytest tests/cli/test_cli.py -v` — все должны пройти
- [x] **Логические тесты** (позитивные):
  - `test_parse_cli_args_minimal_required_args`: передать `["data_dir", "--llm-protocol", "openai", "--llm-url", "http://localhost:11434", "--llm-model", "gpt-4"]` → проверить все 10 свойств (дефолты: env_file=None, index_path=None, llm_token=None, mcp=False, host="0.0.0.0", port=8000)
  - `test_parse_cli_args_all_options`: передать все опции включая `--env-file .env.prod`, `--mcp`, `--port 9000` → проверить все значения
- [x] **Логические тесты** (негативные):
  - `test_parse_cli_args_missing_required_protocol`: без --llm-protocol → SystemExit
  - `test_parse_cli_args_invalid_protocol`: --llm-protocol invalid → SystemExit
- [x] **Логические тесты** (краевые):
  - `test_parse_cli_args_none_argv`: mock sys.argv, вызвать parse_cli_args(None) → использует sys.argv[1:]
- [x] **Отладка**: запустить `pytest tests/cli/test_cli.py -x` — исправлять код, пока все тесты не пройдут
- [x] **Перепроверка контрактов**: проверить что ParseCliResult имеет 10 свойств, parse_cli_args имеет сигнатуру (argv: list[str]|None=None) -> ParseCliResult, оба доступны из sententia.cli
- [x] **Линт**: `ruff check sententia/cli/ tests/cli/` — исправить форматирование

### Task 3: Инфраструктура sententia/config (инфраструктура)

Создать структуру ячейки `sententia/config`: фасад `__init__.py` с реэкспортом `SententiaConfig`. Файл реализации `config.py` с заглушкой.

**КРИТИЧЕСКИ: файлы `CODEMANIFEST` — определения контракта только для чтения. НЕ изменяйте их. Если реализация не соответствует контракту, исправляйте реализацию — никогда не исправляйте контракт.**

- [x] Создать файл `sententia/config/__init__.py` с `__all__`, содержащим `SententiaConfig`
- [x] Создать файл `sententia/config/config.py` с заглушкой класса (pass)
- [x] Проверить доступность фасада: `python -c "from sententia.config import SententiaConfig"`
- [x] Линт: `ruff check sententia/config/` — исправить форматирование при необходимости

### Task 4: Реализация SententiaConfig (TDD)

Реализовать `SententiaConfig` в `sententia/config/config.py` — Pydantic BaseSettings с ENV/env-file поддержкой и cli_overrides приоритетом.

Сущность контракта:
- `SententiaConfig(env_file: str | None = None, cli_overrides: dict[str, Any] | None = None)` — Entity с 9 свойствами

Алгоритм:
```
Pydantic BaseSettings с model_config:
  env_prefix = "SENTENTIA_"
  env_file = env_file или ".env"
  env_file_encoding = "utf-8"
  extra = "ignore"

model_validator(mode="before"):
  apply cli_overrides поверх загруженных ENV/env-file значений

Свойства и дефолты:
  data_dir: str = ""
  index_path: str | None = None
  llm_protocol: str = ""
  llm_url: str = ""
  llm_model: str = ""
  llm_token: str | None = None
  mcp: bool = False
  host: str = "0.0.0.0"
  port: int = 8000
```

Аннотации сущности из CODEMANIFEST (sententia/config):

**SententiaConfig**: Модель конфигурации приложения. Загружает значения из ENV переменных с префиксом SENTENTIA_ и из env-файла. Приоритет источников: `cli_overrides` > ENV > env-файл > дефолты. `env_file`: путь к env-файлу. Если None — используется ".env" по умолчанию. `cli_overrides`: словарь значений из CLI для перекрытия ENV/env-файла. Значения могут быть любого типа (str, int, bool). Использовать `pydantic` для работы с моделью. Использовать `conventions` для правил написания кода и тестов.

**Usages, релевантные для этой задачи:**
- `conventions`: Python 3.10+, kw_only=True, Google-style docstrings, pytest, monkeypatch/tmp_path для тестов
- `pydantic` (путь: `.goga/usages/cooks/pydantic.md`): BaseSettings + SettingsConfigDict для ENV/env-file. Приоритет источников (от высокого к низкому): аргументы конструктора > ENV переменные > env-файл > дефолты. model_validator(mode="before") для дополнительных перекрытий через kwargs. Шаблон:

```python
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env")

    @model_validator(mode="before")
    @classmethod
    def apply_overrides(cls, values: dict) -> dict:
        overrides = values.pop("cli_overrides", None) or {}
        values.update(overrides)
        return values
```

**КРИТИЧЕСКИ: файлы `CODEMANIFEST` — определения контракта только для чтения. НЕ изменяйте их. Если реализация не соответствует контракту, исправляйте реализацию — никогда не исправляйте контракт.**

- [x] **ШАГ 0**: Объявить работу над Task 4 — реализация SententiaConfig
- [x] **Контрактные тесты**: создать `tests/config/__init__.py` и `tests/config/test_config.py`. Проверить: (1) `SententiaConfig` импортируем из `sententia.config`, (2) конструктор принимает `env_file: str|None=None` и `cli_overrides: dict[str,Any]|None=None`, (3) 9 свойств с правильными типами (data_dir: str, index_path: str|None, llm_protocol: str, llm_url: str, llm_model: str, llm_token: str|None, mcp: bool, host: str, port: int)
- [x] **Код**: реализовать `SententiaConfig` как pydantic-settings `BaseSettings` с `SettingsConfigDict(env_prefix="SENTENTIA_", env_file=env_file или ".env", env_file_encoding="utf-8", extra="ignore")` и `model_validator(mode="before")` для cli_overrides
- [x] **Код**: реализовать 9 свойств с дефолтами: data_dir=""", index_path=None, llm_protocol="", llm_url="", llm_model="", llm_token=None, mcp=False, host="0.0.0.0", port=8000
- [x] **Код**: обновить фасад `sententia/config/__init__.py` — реэкспортировать `SententiaConfig`
- [x] **Верификация интерфейсов**: запустить контрактные тесты — `pytest tests/config/test_config.py -v` — все должны пройти
- [x] **Логические тесты** (позитивные):
  - `test_config_defaults`: в чистом окружении (monkeypatch.delenv все SENTENTIA_*) → SententiaConfig() → проверить все 9 дефолтов
  - `test_config_from_env_vars`: monkeypatch.setenv("SENTENTIA_LLM_PROTOCOL", "anthropic"), setenv("SENTENTIA_LLM_URL", "https://api.anthropic.com"), setenv("SENTENTIA_LLM_MODEL", "claude-3") → SententiaConfig() → проверить что ENV-значения загружены
  - `test_config_cli_overrides_take_priority`: monkeypatch.setenv("SENTENTIA_LLM_PROTOCOL", "anthropic"), setenv("SENTENTIA_HOST", "0.0.0.0") → SententiaConfig(cli_overrides={"llm_protocol": "ollama", "host": "127.0.0.1"}) → проверить cli_overrides > ENV
  - `test_config_from_env_file`: tmp_path / ".env" с SENTENTIA_LLM_TOKEN=sk-test-file → SententiaConfig(env_file=str(env_path)) → проверить загрузку из файла
  - `test_config_full_priority_chain`: ENV: SENTENTIA_HOST=10.0.0.1, SENTENTIA_PORT=9000; env-file: SENTENTIA_HOST=10.0.0.2, SENTENTIA_LLM_TOKEN=sk-file; cli_overrides: {"host": "127.0.0.1"} → host="127.0.0.1", port=9000, llm_token="sk-file"
- [x] **Логические тесты** (краевые):
  - `test_config_none_cli_overrides`: SententiaConfig(cli_overrides=None) → defaults
  - `test_config_invalid_cli_overrides_type`: SententiaConfig(cli_overrides={"port": "abc"}) → ValidationError
- [x] **Отладка**: запустить `pytest tests/config/test_config.py -x` — исправлять код, пока все тесты не пройдут
- [x] **Перепроверка контрактов**: проверить что SententiaConfig имеет 9 свойств, конструктор принимает env_file и cli_overrides, приоритет cli_overrides > ENV > env-file > defaults соблюдён
- [x] **Линт**: `ruff check sententia/config/ tests/config/` — исправить форматирование

### Task 5: Переработка main() в __main__.py (TDD)

Переработать `main()` в `sententia/__main__.py` для делегирования в `parse_cli_args` и `SententiaConfig`. Удалить `build_parser()`. Обновить тесты.

Сущность контракта:
- `main(argv: list[str] | None = None) -> void:None` — Routine

Глобальные аннотации CODEMANIFEST sententia (каскадируют в эту задачу):
- Использовать практику `running` для понимания запуска приложения
- Использовать практику `app` из sententia/app для понимания параметров приложения
- Использовать практику `configuration` из sententia/config для понимания создания конфигурации
- Использовать практику `cli` для понимания парсинга CLI аргументов
- Использовать `conventions` для правил написания кода и тестов

Аннотации main routine из CODEMANIFEST:
- Использовать практику `configuration` из sententia/config для создания конфигурации
- Использовать практику `cli` для парсинга CLI аргументов
- Использовать практику `running` для создания, регистрации и запуска приложения

Алгоритм main:
```
1. result = parse_cli_args(argv) → ParseCliResult
2. cli_overrides = {"data_dir": result.data_dir, "index_path": result.index_path, ...}
3. config = SententiaConfig(env_file=result.env_file, cli_overrides=cli_overrides)
4. storage = Storage(config.data_dir)
5. index = Index(storage, config.index_path)
6. IF config.llm_protocol in ("openai", "ollama"): llm = OpenaiProvider(...)
   ELIF config.llm_protocol == "anthropic": llm = AnthropicProvider(...)
   ELSE: raise ValueError(f"Unknown LLM protocol: {config.llm_protocol}")
7. IF config.mcp: MCP tools → SententiaApp → add_mcp_tool × 3 → run
   ELSE: REST resources → SententiaApp → add_rest_resource × 3 → run
8. app.run(host=config.host, port=config.port)
```

**Usages, релевантные для этой задачи:**
- `configuration` из sententia/config (путь: `sententia/config/.usages/configuration.md`): создание SententiaConfig — `config = SententiaConfig(env_file=result.env_file, cli_overrides={...})`, приоритет cli_overrides > ENV > env-файл > дефолты
- `cli` из sententia/cli (путь: `sententia/cli/.usages/cli.md`): `parse_cli_args(argv)` → ParseCliResult, argv=None → sys.argv
- `running` из sententia/app (путь: `sententia/app/.usages/running.md`): регистрация — `app.add_rest_resource(resource)` или `app.add_mcp_tool(tool)`, запуск — `app.run(host="0.0.0.0", port=8000)`. Режим определяется зарегистрированными обработчиками
- `app` из sententia/app (путь: `sententia/app/.usages/app.md`): параметры приложения через SententiaConfig

**КРИТИЧЕСКИ: файлы `CODEMANIFEST` — определения контракта только для чтения. НЕ изменяйте их. Если реализация не соответствует контракту, исправляйте реализацию — никогда не исправляйте контракт.**

- [x] **ШАГ 0**: Объявить работу над Task 5 — переработка main()
- [x] **Контрактные тесты**: обновить `tests/test_main.py`. Проверить: (1) `main` импортируем из `sententia.__main__`, (2) сигнатура main(argv: list[str]|None=None) -> None, (3) `build_parser` больше НЕ импортируем (удалён)
- [x] **Код**: удалить `build_parser()` из `__main__.py`
- [x] **Код**: удалить `sententia/app/.usages/configuration.md` — заменён на `app.md`
- [x] **Код**: переписать `main(argv)` — делегировать в `parse_cli_args(argv)`, сформировать `cli_overrides` из ParseCliResult, создать `SententiaConfig(env_file=result.env_file, cli_overrides=cli_overrides)`, использовать config.* вместо args.* для создания Storage/Index/LLM
- [x] **Код**: добавить матчинг llm_protocol с ValueError для неизвестного протокола
- [x] **Верификация интерфейсов**: запустить контрактные тесты — `pytest tests/test_main.py::TestMainContract -v` — все должны пройти
- [x] **Логические тесты** (позитивные):
  - `test_main_rest_mode`: mock всех зависимостей, main(["data", "--llm-protocol", "openai", "--llm-url", "http://localhost", "--llm-model", "gpt-4"]) → SententiaApp.add_rest_resource.call_count == 3, add_mcp_tool.call_count == 0, run(host="0.0.0.0", port=8000)
  - `test_main_mcp_mode`: mock + "--mcp" → add_mcp_tool.call_count == 3, add_rest_resource.call_count == 0
  - `test_main_with_env_file`: mock + "--env-file" /tmp/custom.env → SententiaConfig called with env_file="/tmp/.../custom.env"
- [x] **Логические тесты** (негативные):
  - `test_main_unknown_protocol_raises_error`: mock parse_cli_args с llm_protocol="invalid" → ValueError("Unknown LLM protocol")
- [x] **Логические тесты** (краевые):
  - `test_main_with_index_path_none`: mock + без --index-path → Index(storage, None)
  - `test_main_with_llm_token_none`: mock + без --llm-token → LLM provider called with token=None
- [x] **Отладка**: запустить `pytest tests/test_main.py -x` — исправлять код, пока все тесты не пройдут
- [x] **Перепроверка контрактов**: main принимает argv, делегирует в parse_cli_args и SententiaConfig, использует config.* для создания компонентов, ValueError для неизвестного протокола
- [x] **Линт**: `ruff check sententia/__main__.py tests/test_main.py` — исправить форматирование

### Task 6: Интеграционные тесты для cli + config + main

Проверить сквозные сценарии взаимодействия parse_cli_args → SententiaConfig → main.

**Usages, релевантные для этой задачи:**
- `conventions`: структура тестов — интеграционные тесты в `tests/`

- [x] Создать/обновить `tests/test_main_integration.py` (если нужно) или дополнить `tests/test_main.py`
- [x] Протестировать полный путь REST: parse_cli_args → cli_overrides → SententiaConfig → Storage → Index → OpenaiProvider → Resources → SententiaApp.run
- [x] Протестировать полный путь MCP: parse_cli_args → cli_overrides → SententiaConfig → Storage → Index → OpenaiProvider → Tools → SententiaApp.run
- [x] Протестировать передачу --env-file через весь стек: parse_cli_args → SententiaConfig(env_file=...)
- [x] Протестировать приоритет конфигурации: ENV + cli_overrides → правильный результат
- [x] Запустить валидацию: `pytest tests/ -x`

---

## Команды валидации

- `pytest tests/cli/ -v`: Тесты sententia/cli ячейки
- `pytest tests/config/ -v`: Тесты sententia/config ячейки
- `pytest tests/test_main.py -v`: Тесты main routine
- `pytest tests/ -x`: Запустить все тесты
- `ruff check sententia/`: Проверка линта
- `python -c "from sententia.cli import ParseCliResult, parse_cli_args"`: Фасад cli
- `python -c "from sententia.config import SententiaConfig"`: Фасад config
- `python -c "from sententia.__main__ import main"`: Фасад main

---

## Критерии завершения

- [x] Каждая сущность контракта реализована в правильном `location` (cli.py, config.py, __main__.py)
- [x] Каждая сущность контракта доступна из фасада (sententia.cli, sententia.config)
- [x] Свойства и методы соответствуют объявленному API
- [x] Описания отражены в поведении (приоритет cli_overrides > ENV > env-file > defaults)
- [x] Зависимости контракта соблюдены (main → parse_cli_args → SententiaConfig)
- [x] Каждая задача кодирования следовала рабочему процессу TDD (контрактные тесты → код → верификация → логические тесты → отладка → перепроверка → линт)
- [x] Контрактные тесты и логические тесты покрывают фасад, API и поведение в рамках каждой задачи кодирования
- [x] Интеграционные тесты существуют для сквозных сценариев cli → config → main
- [x] Ни одна граница пакета не была расширена
- [x] Файлы `CODEMANIFEST` не были изменены (контракт только для чтения)
- [x] Все команды валидации проходят
- [x] Каждая запись Usages упомянута как минимум в одной задаче
