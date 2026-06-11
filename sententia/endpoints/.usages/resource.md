# RESTResource — Abstract Base for HTTP Handlers

## Purpose

`RESTResource` is an abstract base class for REST resources. It defines the HTTP handler contract with get/post/put/delete methods.

## Usage

Subclass `RESTResource` and override the required HTTP method:

```python
class SearchResource(RESTResource):
    url_rule = "/search"

    def post(self, request: SearchRequest) -> SearchResponse:
        # implementation
```

## Registration in FastAPI

```python
router.add_api_route(
    resource.url_rule,
    resource.post,  # bound method
    methods=["POST"],
)
```

## Rules

- Default get/post/put/delete implementations raise NotImplementedError("Method Not Allowed")
- Override only the methods the resource supports
- Property `url_rule` is required
