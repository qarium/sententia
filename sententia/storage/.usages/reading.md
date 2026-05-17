# Чтение файлов

Создайте экземпляр `Storage(directory_path)`.

## Листинг файлов

  files = storage.list_files()
  # → ["docs/auth.md", "docs/setup.md", "guide.md"]

Возвращает список относительных путей всех .md файлов в директории.

## Чтение файла

  content = storage.read_file("docs/auth.md")
  # → {"text": "# Авторизация\n...", "source": "docs/auth.md"}

Если файл не найден — выбрасывается FileNotFoundError.
Путь file_path должен быть относительным, выход за пределы directory_path запрещён.
