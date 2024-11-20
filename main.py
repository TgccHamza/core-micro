import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, status
from app.routers import project
from app.routers import arena
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from typing import Dict, Any
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db, DATABASE_URL
from alembic.config import Config
from alembic import command
from fastapi.middleware.cors import CORSMiddleware


import tempfile

print("Temp directory before changing it:", tempfile.gettempdir())
tempfile.tempdir = "/app/tmp_uploads"
print("Temp directory after changing it:", tempfile.gettempdir())

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/server/migrate")
async def run_migrations():
    """Endpoint to run Alembic migrations."""
    try:
        alembic_path = '/app/app/alembic.ini'
        alembic_cfg = Config(alembic_path)
        alembic_cfg.set_main_option('sqlalchemy.url', DATABASE_URL.replace('%', '%%'))
        command.upgrade(alembic_cfg, "head")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Migrations applied successfully"}
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"Migration failed: {e}"}
        )


@app.post("/server/generate-migration")
async def generate_migrations():
    """Endpoint to run Alembic migrations."""
    try:
        alembic_path = '/app/app/alembic.ini'

        alembic_cfg = Config(alembic_path)
        alembic_cfg.set_main_option('sqlalchemy.url', DATABASE_URL.replace('%', '%%'))
        command.revision(alembic_cfg, autogenerate=True)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Migrations has been generated"}
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"Migration failed to generate: {e}"}
        )


@app.get("/health", response_model=Dict[str, Any])
async def health_game(db: Session = Depends(get_db)):
    try:
        # Attempt to execute a simple query to check if the database connection works
        db.execute(text("SELECT 1"))
        return JSONResponse(content={'status': 'Healthy', 'message': 'Database connected successfully'})
    except Exception as e:
        print(f"error ==> {str(e)} \n")
        DB_USER = os.getenv("DB_USER", "user")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
        DB_HOST = os.getenv("DB_HOST", "db")
        DB_NAME = os.getenv("DB_NAME", "db_name")
        DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        print(f"DB_USER: {DB_USER}\n")
        print(f"DB_PASSWORD: {DB_PASSWORD}\n")
        print(f"DB_HOST: {DB_HOST}\n")
        print(f"DB_NAME: {DB_NAME}\n")
        print(f"DATABASE_URL: {DATABASE_URL}\n")
        # Handle exceptions related to database connectivity
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={'status': 'Unhealthy', 'message': 'Database connection failed', 'error': str(e)}
        )


app.include_router(project.client_router, tags=["Client Apis"])
app.include_router(project.admin_router, tags=["Orchestrator Apis"])
app.include_router(arena.router, tags=["Orchestrator Apis", "Client Apis"])


@app.get("/openapi-client.json", include_in_schema=False)
async def get_admin_openapi_json():
    return custom_openapi(['client'])


# Custom endpoint for Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    app.openapi_schema = custom_openapi(["client"])
    segment_micro = os.getenv("SEGMENT_MICRO", "")
    if segment_micro != "" and not segment_micro.startswith("/"):
        segment_micro = f"/{segment_micro}"
    return get_swagger_ui_html(
        openapi_url=f"{segment_micro}/openapi-client.json",
        title="TGCC - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )


# Custom OpenAPI Schemas for Each Category
def custom_openapi(schema_tags):
    openapi_schema = get_openapi(
        title="Custom API",
        version="1.0.0",
        description="Custom split OpenAPI schema for admin, client, and server",
        routes=[route for route in app.routes if any(tag in schema_tags for tag in route.tags)]
    )

    segment_micro = os.getenv("SEGMENT_MICRO", "")
    for path in list(openapi_schema["paths"].keys()):
        openapi_schema["paths"][f"{segment_micro}{path}"] = openapi_schema["paths"].pop(path)

    return openapi_schema
