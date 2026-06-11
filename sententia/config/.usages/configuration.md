# Application Configuration

SententiaConfig is a configuration model that resolves values from environment variables and a dotenv file.

## Instantiation

Default instantiation — resolves values from ENV and the `.env` file:

```python
from sententia.config import SententiaConfig

config = SententiaConfig()
```

With a custom dotenv file:

```python
config = SententiaConfig(env_file="/path/to/.env")
```

## CLI Overrides

Pass CLI arguments as overrides:

```python
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
```

Resolution priority: cli_overrides > ENV > dotenv file > built-in defaults.

## Environment Variables

| Variable                | Field        | Default   |
|-------------------------|-------------|-----------|
| SENTENTIA_DATA_DIR      | data_dir    | ""        |
| SENTENTIA_INDEX_PATH    | index_path  | None      |
| SENTENTIA_LLM_PROTOCOL  | llm_protocol| ""        |
| SENTENTIA_LLM_URL       | llm_url     | ""        |
| SENTENTIA_LLM_MODEL     | llm_model   | ""        |
| SENTENTIA_LLM_TOKEN     | llm_token   | ""        |
| SENTENTIA_MCP           | mcp         | False     |
| SENTENTIA_HOST          | host        | "0.0.0.0" |
| SENTENTIA_PORT          | port        | 8000      |
