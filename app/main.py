from fastapi import FastAPI, Depends, status
from .database import engine, Base
from .routers import project
from .routers import arena
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from typing import Dict, Any
import os
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from sqlalchemy import text
from .database import get_db

# Base.metadata.create_all(bind=engine)

app = FastAPI(docs_url=None)


# Custom endpoint for Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    segment_micro = os.getenv("SEGMENT_MICRO", "")
    if segment_micro != "" and not segment_micro.startswith("/"):
        segment_micro = f"/{segment_micro}"
    return get_swagger_ui_html(
        openapi_url=f"{segment_micro}/openapi.json",
        title="TGCC - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )


@app.get("/health", response_model=Dict[str, Any])
async def health_game(db: Session = Depends(get_db)):
    try:
        # Attempt to execute a simple query to check if the database connection works
        db.execute(text("SELECT 1"))
        return JSONResponse(content={'status': 'Healthy', 'message': 'Database connected successfully'})
    except Exception as e:
        # Handle exceptions related to database connectivity
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={'status': 'Unhealthy', 'message': 'Database connection failed', 'error': str(e)}
        )


app.include_router(project.router, tags=["projects"])
app.include_router(arena.router, tags=["arenas"])


# Customize the OpenAPI schema to include "/gamicore" in the paths
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Custom API",
        version="1.0.0",
        description="This is a custom OpenAPI schema",
        routes=app.routes,
    )
    for path in list(openapi_schema["paths"].keys()):
        segment_micro = os.getenv("SEGMENT_MICRO", "")
        openapi_schema["paths"][f"{segment_micro}{path}"] = openapi_schema["paths"].pop(path)
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
