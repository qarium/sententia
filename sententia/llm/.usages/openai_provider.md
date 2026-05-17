# OpenaiProvider — создание провайдера

Создайте экземпляр OpenaiProvider с конфигурацией.

Параметры:
- url: str — URL API endpoint
- model: str — идентификатор модели
- token: str | None — API-ключ (необязательный)

Пример:
  provider = OpenaiProvider(url="https://api.openai.com", model="gpt-4", token="sk-...")