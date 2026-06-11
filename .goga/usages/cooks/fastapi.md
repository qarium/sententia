# FastAPI — a framework for HTTP API

## Creating an application

```python
from fastapi import FastAPI

app = FastAPI(title="Knowage API")
```

## APIRouter and route registration

Bind a class instance as a route handler via a bound method. The endpoint object must expose: `url_rule` (str property), `method` (str property), and `handle` (callable method).

```python
from fastapi import APIRouter

router = APIRouter()

# endpoint — a class instance with properties url_rule, method and method handle
router.add_api_route(
    endpoint.url_rule,           # "/search"
    endpoint.handle,             # bound method
    methods=[endpoint.method],   # ["POST"]
)
```

Connect the router to the application:

```python
app.include_router(router)
```

## POST with body (Pydantic model)

```python
@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    return SearchResponse(results=[])
```

## GET with path parameter

The `{param:path}` syntax captures the entire remaining URL path including forward slashes:

```python
@router.get("/files/{file_path:path}", response_model=FileResponse)
async def get_file(file_path: str) -> FileResponse:
    return FileResponse(text="...", source=file_path)
```

## Running via uvicorn

```python
import uvicorn

uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Exception handling

```python
from fastapi import HTTPException

# In an endpoint — raise, never return
raise HTTPException(status_code=404, detail="File not found")

# Global exception handler
@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})
```