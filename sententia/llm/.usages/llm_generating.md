# Базовый паттерн работы с LLM-провайдером

Все провайдеры реализуют единый интерфейс generate(prompt: str) -> str.

Использование:
  answer = llm_provider.generate("Ваш промпт")