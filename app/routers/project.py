# router/project.py
import os
from typing import Dict, Any

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.helpers import get_jwt_claims
from app.middlewares.ClientAuthMiddleware import ClientAuthMiddleware
from app.middlewares.CollabAuthMiddleware import CollabAuthMiddleware
from app.middlewares.MiddlewareWrapper import middlewareWrapper
from app.payloads.request.ModuleCreateRequest import ModuleCreateRequest
from app.payloads.request.ModuleUpdateRequest import ModuleUpdateRequest
from app.payloads.request.ProjectCreateRequest import ProjectCreateRequest
from app.payloads.request.ProjectUpdateRequest import ProjectUpdateRequest
from app.payloads.response.EspaceAdminClientResponse import AdminSpaceClientResponse
from app.payloads.response.FavoriteResponse import FavoriteResponse
from app.payloads.response.GameViewClientResponse import GameViewClientResponse
from app.payloads.response.ModuleAdminResponse import ModuleAdminResponse
from app.payloads.response.ProjectAdminResponse import ProjectAdminResponse
from app.payloads.response.ProjectClientWebResponse import ProjectClientWebResponse
from app.routers import filepb2
from app.routers import filegrpc
from app.database import get_db
from app.services import project as services
import grpc

admin_router = APIRouter(
    route_class=middlewareWrapper(middlewares=[CollabAuthMiddleware])
)

client_router = APIRouter(
    route_class=middlewareWrapper(middlewares=[ClientAuthMiddleware])
)


@admin_router.get("/projects", response_model=list[ProjectAdminResponse])
def get_projects(db: Session = Depends(get_db)):
    """Endpoint to list all projects."""
    return services.list_projects(db)


@admin_router.get("/projects/{project_id}/modules", response_model=list[ModuleAdminResponse])
def get_project_modules(project_id: str, db: Session = Depends(get_db)):
    """Endpoint to list all modules for a specific project."""
    return services.list_modules(db, project_id)


# Project Endpoints
@admin_router.post("/projects", response_model=ProjectAdminResponse)
def create_project(project: ProjectCreateRequest, db: Session = Depends(get_db)):
    return services.create_project(db, project)


@admin_router.get("/projects/{project_id}", response_model=ProjectAdminResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    return services.get_project(db, project_id)


@admin_router.put("/projects/{project_id}", response_model=ProjectAdminResponse)
def update_project(project_id: str, project: ProjectUpdateRequest, db: Session = Depends(get_db)):
    return services.update_project(db, project_id, project)


@admin_router.delete("/projects/{project_id}", response_model=dict)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    return services.delete_project(db, project_id)


# ProjectModule Endpoints
@admin_router.post("/modules", response_model=ModuleAdminResponse)
def create_module(module: ModuleCreateRequest, db: Session = Depends(get_db)):
    return services.create_module(db, module)


@admin_router.get("/modules/{module_id}", response_model=ModuleAdminResponse)
def get_module(module_id: str, db: Session = Depends(get_db)):
    return services.get_module(db, module_id)


@admin_router.put("/modules/{module_id}", response_model=ModuleAdminResponse)
def update_module(module_id: str, module: ModuleUpdateRequest, db: Session = Depends(get_db)):
    return services.update_module(db, module_id, module)


@admin_router.delete("/modules/{module_id}", response_model=dict)
def delete_module(module_id: str, db: Session = Depends(get_db)):
    return services.delete_module(db, module_id)


@admin_router.post("/modules/{module_id}/upload")
async def upload_file(module_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return {"message": "No upload file sent"}
    if not file:
        return {"message": "No upload file sent"}

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


@client_router.get("/espace-admin", response_model=AdminSpaceClientResponse)
def admin_space(jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims), db: Session = Depends(get_db)):
    org_id = jwt_claims.get("org_id")
    user_id = jwt_claims.get("uid")
    return services.espaceAdmin(db=db, user_id=user_id, org_id=org_id)


@client_router.get("/game-view/{game_id}", response_model=GameViewClientResponse)
def game_view(game_id: str, jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims), db: Session = Depends(get_db)):
    org_id = jwt_claims.get("org_id")
    return services.gameView(db=db, org_id=org_id, game_id=game_id)


@client_router.post("/projects/{project_id}/favorite", response_model=FavoriteResponse)
def favorite_project(project_id: str, jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
                     db: Session = Depends(get_db)):
    """Endpoint to add a project to favorites."""

    user_id = jwt_claims.get("uid")
    return services.favorite_project(db=db, user_id=user_id, project_id=project_id)


@client_router.delete("/projects/{project_id}/favorite")
def unfavorite_project(project_id: str, jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
                       db: Session = Depends(get_db)):
    """Endpoint to remove a project from favorites."""

    user_id = jwt_claims.get("uid")

    return services.unfavorite_project(db=db, user_id=user_id, project_id=project_id)


@client_router.get("/users/{user_id}/favorites", response_model=list[ProjectClientWebResponse])
def list_favorites(jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims), db: Session = Depends(get_db)):
    """Endpoint to list all favorite projects of a user."""
    user_id = jwt_claims.get("uid")
    return services.list_favorites(db=db, user_id=user_id)
