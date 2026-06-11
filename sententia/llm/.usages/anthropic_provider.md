# AnthropicProvider — Creating a Provider

Create an AnthropicProvider instance with configuration.

Parameters:
- url: str — API endpoint URL
- model: str — model identifier
- token: str | None — API key (optional)

Example:
  provider = AnthropicProvider(url="https://api.anthropic.com", model="claude-3-sonnet", token="sk-ant-...")
