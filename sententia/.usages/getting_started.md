# Быстрый старт

Запуск сервиса из командной строки:

  python -m sententia /path/to/markdown/docs \
    --llm-protocol openai \
    --llm-url https://api.openai.com \
    --llm-model gpt-4 \
    --llm-token sk-...

Локальный запуск через Ollama (без токена):

  python -m sententia /path/to/markdown/docs \
    --llm-protocol ollama \
    --llm-url http://localhost:11434 \
    --llm-model llama3

После запуска API доступно на http://localhost:8000