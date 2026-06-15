# FastAPI — a framework for HTTP API

## Creating an application

```python
from fastapi import FastAPI

app = FastAPI(title="Knowage API")
```

## Route registration on the application

Register a route directly on the `FastAPI` instance when the caller wants each route to appear in `app.routes` as a flat `APIRoute` with `.path` and `.methods`. Prefer this form when registering handlers bound to class instances.

```python
# endpoint — a class instance with a str property `url_rule` and a bound method `handle`
app.add_api_route(
    endpoint.url_rule,           # "/search"
    endpoint.handle,             # bound method
    methods=["POST"],
)
```

Direct registration via `app.add_api_route(...)` keeps `app.routes` flat across the supported `fastapi>=0.100` range (including 0.136.1 and 0.137.0).

## Router composition with APIRouter

Group routes into an `APIRouter` and attach the whole group to the application. Use this form when routes are assembled in a separate module and composed into the app as a unit.

```python
from fastapi import APIRouter

router = APIRouter()

router.add_api_route(
    endpoint.url_rule,           # "/search"
    endpoint.handle,             # bound method
    methods=[endpoint.method],   # ["POST"]
)

app.include_router(router)
```

In FastAPI 0.137+ (Starlette 1.x), `app.include_router(router)` keeps the attached router in `app.routes` as a lazy `_IncludedRouter` wrapper. Such entries expose neither `.path` nor `.methods` until request matching unfolds them. Do not read `app.routes` expecting a flat list of `Route`/`APIRoute` when routes are attached via `include_router` — use direct registration via `app.add_api_route(...)` instead.

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