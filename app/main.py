from fastapi import FastAPI
from .database import engine, Base
from .routers import project
from .routers import arena
from fastapi.openapi.docs import get_swagger_ui_html

#Base.metadata.create_all(bind=engine)

app = FastAPI(docs_url=None)

# Custom endpoint for Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title="TGCC - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

app.include_router(project.router, tags=["projects"])
app.include_router(arena.router, tags=["arenas"])
