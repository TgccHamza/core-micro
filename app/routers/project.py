# router/project.py
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.helpers import get_jwt_claims
import logging

from app.payloads.response.GameViewModeratorClientResponse import GameViewModeratorClientResponse
from app.payloads.response.GameViewPlayerClientResponse import GameViewPlayerClientResponse

logger = logging.getLogger(__name__)
from app.middlewares.ClientAuthMiddleware import ClientAuthMiddleware
from app.middlewares.CollabAuthMiddleware import CollabAuthMiddleware
from app.middlewares.MiddlewareWrapper import middlewareWrapper
from app.payloads.request.GameUpdateRequest import GameUpdateRequest
from app.payloads.request.ModuleCreateRequest import ModuleCreateRequest
from app.payloads.request.ModuleUpdateRequest import ModuleUpdateRequest
from app.payloads.request.ProjectCommentCreateRequest import ProjectCommentCreateRequest
from app.payloads.request.ProjectCommentUpdateRequest import ProjectCommentUpdateRequest
from app.payloads.request.ProjectCreateRequest import ProjectCreateRequest
from app.payloads.request.ProjectUpdateRequest import ProjectUpdateRequest
from app.payloads.response.EspaceAdminClientResponse import AdminSpaceClientResponse
from app.payloads.response.FavoriteResponse import FavoriteResponse
from app.payloads.response.GameConfigResponse import GameConfigResponse
from app.payloads.response.GameViewClientResponse import GameViewClientResponse
from app.payloads.response.ModuleAdminResponse import ModuleAdminResponse
from app.payloads.response.ProjectAdminResponse import ProjectAdminResponse
from app.payloads.response.ProjectClientWebResponse import ProjectClientWebResponse
from app.payloads.response.ProjectCommentResponse import ProjectCommentResponse
from app.database import get_db_async
from app.services import project as services
from app.services import create_project as services_create_project
from app.services import get_project as services_get_project
from app.services import space_admin as services_space_admin
from app.services import space_user as services_space_user
from app.services import game_view as services_game_view
from app.services import game_view_user as services_game_view_user
from app.services import favorite_project as services_favorite_project
from app.services import unfavorite_project as services_unfavorite_project
from app.services import list_favorites as services_list_favorites
from app.services import config_client_game as services_config_client_game
from app.services import update_client_game as services_update_client_game
from app.services import create_comment as services_create_comment
from app.services import list_comments as services_list_comments
from app.services import update_comment as services_update_comment
from app.services import delete_comment as services_delete_comment
from app.services import like_comment as services_like_comment
from app.services import dislike_comment as services_dislike_comment

admin_router = APIRouter(
    route_class=middlewareWrapper(middlewares=[CollabAuthMiddleware])
)



@admin_router.get("/projects", response_model=list[ProjectAdminResponse])
async def get_projects(db: AsyncSession = Depends(get_db_async)):
    """Endpoint to list all projects."""
    return await services.list_projects(db)


@admin_router.get("/projects/{project_id}/modules", response_model=list[ModuleAdminResponse])
async def get_project_modules(project_id: str, db: AsyncSession = Depends(get_db_async)):
    """Endpoint to list all modules for a specific project."""
    return await services.list_modules(db, project_id)


# Project Endpoints
@admin_router.post("/projects", response_model=ProjectAdminResponse)
async def create_project(project: ProjectCreateRequest, db: AsyncSession = Depends(get_db_async)):
    return await services_create_project.create_project(db, dict(project))


@admin_router.get("/projects/{project_id}", response_model=ProjectAdminResponse)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db_async)):
    return await services_get_project.get_project(db, project_id)


@admin_router.put("/projects/{project_id}", response_model=ProjectAdminResponse)
async def update_project(project_id: str, project: ProjectUpdateRequest, db: AsyncSession = Depends(get_db_async)):
    return await services.update_project(db, project_id, project)


@admin_router.delete("/projects/{project_id}", response_model=dict)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db_async)):
    return await services.delete_project(db, project_id)

