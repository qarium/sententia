# AnthropicProvider — создание провайдера

Создайте экземпляр AnthropicProvider с конфигурацией.

Параметры:
- url: str — URL API endpoint
- model: str — идентификатор модели
- token: str | None — API-ключ (необязательный)

Пример:
  provider = AnthropicProvider(url="https://api.anthropic.com", model="claude-3-sonnet", token="sk-ant-...")