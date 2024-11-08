from fastapi import FastAPI, Request
from .database import engine, Base
from .routers import project
from .routers import arena
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from typing import Dict, Any

# Base.metadata.create_all(bind=engine)

app = FastAPI(docs_url=None)


# Custom endpoint for Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    path_segments = request.url.path.strip("/").split("/")
    first_segment = f"/{path_segments[0]}" if path_segments else ""
    return get_swagger_ui_html(
        openapi_url=f"{first_segment}/openapi.json",
        title="TGCC - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )


@app.get("/health", response_model=Dict[str, Any])
async def health_game():
    return JSONResponse(content={'msg': 'Hello world'})


app.include_router(project.router, tags=["projects"])
app.include_router(arena.router, tags=["arenas"])
