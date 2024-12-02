import mimetypes
import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, status, HTTPException
from app.routers import project
from app.routers import arena
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from typing import Dict, Any
from fastapi.openapi.utils import get_openapi
from sqlalchemy import text
from app.database import get_db_async, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from alembic.config import Config
from alembic import command
from fastapi.middleware.cors import CORSMiddleware

import os

import tempfile
import logging

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
log_file = "uvicorn_logs.log"
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file),  # Save logs to a file
                        logging.StreamHandler()  # Also log to console
                    ])

logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

print("Change tmp folder for uploading file")
# actualy he take the file in memory only
tempfile.tempdir = "/app/tmp_uploads"

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.post("/create-folder")
# async def create_folder():
#     try:
#         # Static folder path
#         folder_path = Path("/app/tmp_uploads")
#
#         # Create the folder if it doesn't exist
#         folder_path.mkdir(parents=True, exist_ok=True)
#
#         # Set full permissions (777 equivalent)
#         os.chmod(folder_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
#
#         # Get folder metadata
#         folder_stat = folder_path.stat()
#         folder_logs = {
#             "folder_path": str(folder_path.resolve()),
#             "permissions": oct(folder_stat.st_mode)[-3:],  # Last 3 digits of octal permission
#             "creation_time": folder_stat.st_ctime,
#             "is_directory": folder_path.is_dir()
#         }
#
#         return {"message": "Folder created successfully", "logs": folder_logs}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error creating folder: {str(e)}")

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
async def health_game(db: AsyncSession = Depends(get_db_async)):
    try:
        # Attempt to execute a simple query to check if the database connection works
        await db.execute(text("SELECT 1"))
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
    return custom_openapi('Client Apis')


# Custom endpoint for Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
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
def custom_openapi(schema_tag):
    routes = []
    for route in app.routes:
        if schema_tag in route.tags:
            route.tags = [schema_tag]
            routes.append(route)

    openapi_schema = get_openapi(
        title="Custom API",
        version="1.0.0",
        description="Custom split OpenAPI schema for admin, client, and server",
        routes=routes
    )

    segment_micro = os.getenv("SEGMENT_MICRO", "")
    for path in list(openapi_schema["paths"].keys()):
        openapi_schema["paths"][f"{segment_micro}{path}"] = openapi_schema["paths"].pop(path)

    return openapi_schema


# from pathlib import Path
# import stat
# from pydantic import BaseModel

# # Pydantic model for the request body
# class DirectoryRequest(BaseModel):
#     directory_path: str
#
# # Function to get the file or directory permissions in a readable format
# def get_permissions(path: str) -> dict[str, bool]:
#     file_stat = os.stat(path)
#     permissions = {
#         'read': bool(file_stat.st_mode & stat.S_IRUSR),
#         'write': bool(file_stat.st_mode & stat.S_IWUSR),
#         'execute': bool(file_stat.st_mode & stat.S_IXUSR),
#     }
#     return permissions
#
#
# @app.post("/scan-directory")
# async def scan_directory(request: DirectoryRequest):
#     directory_path = request.directory_path
#
#     if not os.path.exists(directory_path):
#         logger.error(f"Directory {directory_path} does not exist.")
#         raise HTTPException(status_code=400, detail=f"Directory {directory_path} does not exist.")
#
#     if not os.path.isdir(directory_path):
#         logger.error(f"{directory_path} is not a valid directory.")
#         raise HTTPException(status_code=400, detail=f"{directory_path} is not a valid directory.")
#
#     try:
#         files_and_dirs = os.listdir(directory_path)
#     except PermissionError:
#         logger.error(f"Permission denied to access directory {directory_path}.")
#         raise HTTPException(status_code=403, detail="Permission denied to access this directory.")
#
#     results = []
#     for item in files_and_dirs:
#         item_path = os.path.join(directory_path, item)
#         permissions = get_permissions(item_path)
#         results.append({
#             "name": item,
#             "permissions": permissions
#         })
#
#     logger.info(f"Scanned directory: {directory_path}")
#     return {"directory": directory_path, "files_and_directories": results}


# Endpoint to get the logs from the log file
@app.get("/get-logs")
async def get_logs():
    if not os.path.exists(log_file):
        logger.error(f"Log file {log_file} does not exist.")
        raise HTTPException(status_code=404, detail="Log file not found.")

    # Return the log file as response
    try:
        return FileResponse(log_file, media_type='text/plain', filename=log_file)
    except Exception as e:
        logger.error(f"Error reading log file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error reading log file.")


# Endpoint to get the logs from the log file
@app.get("/assets/{file_name}")
async def get_file_from_assets(file_name: str):
    # Define the assets directory path
    assets_dir = os.path.join('/app/app', "assets")

    # Construct the full file path
    file_path = os.path.join(assets_dir, file_name)

    # Check if the file exists and is a file (not a directory)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Guess the MIME type of the file
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"  # Default MIME type

    # Return the file using FileResponse
    return FileResponse(file_path, media_type=mime_type, filename=file_name,  # Optional, for download prompt
                        headers={"Content-Disposition": f"inline; filename={file_name}"})
