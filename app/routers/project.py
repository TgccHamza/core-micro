# router/project.py
import os

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from . import filepb2
from . import filegrpc
from .. import schemas
from ..database import get_db
from ..services import project as services
import grpc

router = APIRouter()

@router.get("/projects/", response_model=list[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    """Endpoint to list all projects."""
    return services.list_projects(db)

@router.get("/projects/{project_id}/modules/", response_model=list[schemas.ModuleResponse])
def get_project_modules(project_id: str, db: Session = Depends(get_db)):
    """Endpoint to list all modules for a specific project."""
    return services.list_modules(db, project_id)

# Project Endpoints
@router.post("/projects/", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return services.create_project(db, project)

@router.get("/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    return services.get_project(db, project_id)

@router.put("/projects/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: str, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    return services.update_project(db, project_id, project)

@router.delete("/projects/{project_id}", response_model=dict)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    return services.delete_project(db, project_id)

# ProjectModule Endpoints
@router.post("/modules/", response_model=schemas.ModuleResponse)
def create_module(module: schemas.ModuleCreate, db: Session = Depends(get_db)):
    return services.create_module(db, module)

@router.get("/modules/{module_id}", response_model=schemas.ModuleResponse)
def get_module(module_id: str, db: Session = Depends(get_db)):
    return services.get_module(db, module_id)

@router.put("/modules/{module_id}", response_model=schemas.ModuleResponse)
def update_module(module_id: str, module: schemas.ModuleUpdate, db: Session = Depends(get_db)):
    return services.update_module(db, module_id, module)

@router.delete("/modules/{module_id}", response_model=dict)
def delete_module(module_id: str, db: Session = Depends(get_db)):
    return services.delete_module(db, module_id)

@router.post("/modules/{module_id}/upload")
async def upload_file(module_id: str, file: UploadFile, db: Session = Depends(get_db)):
    # Read the file data
    file_data = await file.read()

    # Connect to the gRPC server
    grpc_container = os.getenv("GRPC_CONTAINER", "grpc_url")
    grpc_port = os.getenv("GRPC_PORT", "50051")
    with grpc.insecure_channel(f"{grpc_container}:{grpc_port}") as channel:
        # Update the stub to use the TemplateService
        stub = filegrpc.TemplateServiceStub(channel)
        # Create the request with the updated message type and fields
        request = filepb2.UploadFileRequest(file_data=file_data, filename=file.filename)
        response = stub.UploadFile(request)
        # Return the response data
        return services.set_template_module(db, module_id, response.file_id)