# FastAPI — фреймворк для HTTP API

## Создание приложения

```python
from fastapi import FastAPI

app = FastAPI(title="Knowage API")
```

## APIRouter и регистрация маршрутов

Привязка экземпляра класса как route handler через bound-метод:

```python
from fastapi import APIRouter

router = APIRouter()

# endpoint — экземпляр класса с properties url_rule, method и методом handle
router.add_api_route(
    endpoint.url_rule,           # "/search"
    endpoint.handle,             # bound method
    methods=[endpoint.method],   # ["POST"]
)
```

Подключение роутера к приложению:

```python
app.include_router(router)
```

## POST с body (Pydantic моделью)

```python
@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    return SearchResponse(results=[])
```

## GET с path parameter

Синтаксис `{param:path}` захватывает весь остаток URL включая слеши:

```python
@router.get("/files/{file_path:path}", response_model=FileResponse)
async def get_file(file_path: str) -> FileResponse:
    return FileResponse(text="...", source=file_path)
```

## Запуск через uvicorn

```python
import uvicorn

uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Обработка исключений

```python
from fastapi import HTTPException

# В endpoint — raise, не return
raise HTTPException(status_code=404, detail="File not found")

# Глобальный обработчик
@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})
```
