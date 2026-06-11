# OpenaiProvider — Creating a Provider

Create an OpenaiProvider instance with configuration.

Parameters:
- url: str — API endpoint URL
- model: str — model identifier
- token: str | None — API key (optional)

Example:
  provider = OpenaiProvider(url="https://api.openai.com", model="gpt-4", token="sk-...")
