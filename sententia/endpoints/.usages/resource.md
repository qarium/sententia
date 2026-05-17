# RESTResource — базовый тип HTTP-обработчика

## Назначение

`RESTResource` — базовый тип для REST-ресурсов. Определяет контракт HTTP-обработчика с методами get/post/put/delete.

## Использование

Создайте подкласс `RESTResource`, переопределив нужный HTTP-метод:

```python
class SearchResource(RESTResource):
    url_rule = "/search"

    def post(self, request: SearchRequest) -> SearchResponse:
        # реализация
```

## Регистрация в FastAPI

```python
router.add_api_route(
    resource.url_rule,
    resource.post,  # bound method
    methods=["POST"],
)
```

## Правила

- Базовые реализации get/post/put/delete возвращают Method Not Allowed
- Переопределяйте только нужные методы
- Свойство `url_rule` обязательно
