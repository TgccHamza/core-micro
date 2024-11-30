# router/project.py
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.helpers import get_jwt_claims
import logging

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

client_router = APIRouter(
    route_class=middlewareWrapper(middlewares=[ClientAuthMiddleware])
)


@admin_router.get("/projects", response_model=list[ProjectAdminResponse])
async def get_projects(db: AsyncSession = Depends(get_db_async)):
    """Endpoint to list all projects."""
    return await services.list_projects(db)


@admin_router.get("/projects/{project_id}/modules", response_model=list[ModuleAdminResponse])
def get_project_modules(project_id: str, db: AsyncSession = Depends(get_db_async)):
    """Endpoint to list all modules for a specific project."""
    return services.list_modules(db, project_id)


# Project Endpoints
@admin_router.post("/projects", response_model=ProjectAdminResponse)
async def create_project(project: ProjectCreateRequest, db: AsyncSession = Depends(get_db_async)):
    return await services_create_project.create_project(db, dict(project))


@admin_router.get("/projects/{project_id}", response_model=ProjectAdminResponse)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db_async)):
    return await services_get_project.get_project(db, project_id)


@admin_router.put("/projects/{project_id}", response_model=ProjectAdminResponse)
def update_project(project_id: str, project: ProjectUpdateRequest, db: AsyncSession = Depends(get_db_async)):
    return services.update_project(db, project_id, project)


@admin_router.delete("/projects/{project_id}", response_model=dict)
def delete_project(project_id: str, db: AsyncSession = Depends(get_db_async)):
    return services.delete_project(db, project_id)


# ProjectModule Endpoints
@admin_router.post("/modules", response_model=ModuleAdminResponse)
def create_module(module: ModuleCreateRequest, db: AsyncSession = Depends(get_db_async)):
    return services.create_module(db, module)


@admin_router.get("/modules/{module_id}", response_model=ModuleAdminResponse)
def get_module(module_id: str, db: AsyncSession = Depends(get_db_async)):
    return services.get_module(db, module_id)


@admin_router.put("/modules/{module_id}", response_model=ModuleAdminResponse)
def update_module(module_id: str, module: ModuleUpdateRequest, db: AsyncSession = Depends(get_db_async)):
    return services.update_module(db, module_id, module)


@admin_router.delete("/modules/{module_id}", response_model=dict)
def delete_module(module_id: str, db: AsyncSession = Depends(get_db_async)):
    return services.delete_module(db, module_id)


@admin_router.post("/modules/{module_id}/set-template")
async def set_template_module(module_id: str, template_id: str,
                              db: AsyncSession = Depends(get_db_async)):
    try:
        return services.set_template_module(db, module_id, template_id)
    except Exception as e:
        logging.error(f"Error in upload_file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@client_router.get("/espace-admin", response_model=AdminSpaceClientResponse)
async def admin_space(
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
        db: AsyncSession = Depends(get_db_async)
):
    """
    Endpoint to retrieve admin space information for a client.

    This endpoint fetches the admin space details for the client based on JWT claims,
    which include the organization ID (org_id) and user ID (uid). It calls the `espaceAdmin`
    service to retrieve the necessary data from the database.

    Parameters:
    - jwt_claims (Dict): The JWT claims, which include the `org_id` and `uid`.
    - db (AsyncSession): The database AsyncSession, injected through dependency.

    Returns:
    - AdminSpaceClientResponse: The response model containing admin space details.

    Raises:
    - HTTPException: If `org_id` or `uid` is missing from the JWT claims or if a database error occurs.
    """
    try:
        org_id = jwt_claims.get("org_id")
        user_id = jwt_claims.get("uid")
        role = jwt_claims.get("role")

        if not org_id or not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing 'org_id' or 'uid' in JWT claims"
            )
        if role == "admin":
            # Call the service function to retrieve the admin space data
            admin_space_data = await services_space_admin.space_admin(db=db, user_id=user_id, org_id=org_id)
        else:
            admin_space_data = await services_space_user.space_user(db=db, user_id=user_id, org_id=org_id)

        if admin_space_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin space data not found"
            )

        return admin_space_data

    except Exception as e:
        # Log the error (you can use a proper logging framework in your project)
        logger.error(f"Error in admin_space: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request {e}"
        )


@client_router.get("/game-view/{game_id}", response_model=GameViewClientResponse)
async def game_view(game_id: str, jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
                    db: AsyncSession = Depends(get_db_async)):
    try:
        org_id = jwt_claims.get("org_id")
        role = jwt_claims.get("role")
        if role == "admin":
            return await services_game_view.gameView(db=db, org_id=org_id, game_id=game_id)
        else:
            return await services_game_view.gameView(db=db, org_id=org_id, game_id=game_id)
    except Exception as e:
        # Log the error (you can use a proper logging framework in your project)
        logger.error(f"Error in game_view: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request {e}"
        )


@client_router.post("/projects/{project_id}/favorite", response_model=FavoriteResponse)
def favorite_project(project_id: str, jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
                     db: AsyncSession = Depends(get_db_async)):
    """Endpoint to add a project to favorites."""

    user_id = jwt_claims.get("uid")
    return services_favorite_project.favorite_project(db=db, user_id=user_id, project_id=project_id)


@client_router.delete("/projects/{project_id}/favorite")
def unfavorite_project(project_id: str, jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
                       db: AsyncSession = Depends(get_db_async)):
    """Endpoint to remove a project from favorites."""

    user_id = jwt_claims.get("uid")

    return services_unfavorite_project.unfavorite_project(db=db, user_id=user_id, project_id=project_id)


@client_router.get("/users/{user_id}/favorites", response_model=list[ProjectClientWebResponse])
def list_favorites(jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims), db: AsyncSession = Depends(get_db_async)):
    """Endpoint to list all favorite projects of a user."""
    user_id = jwt_claims.get("uid")
    return services_list_favorites.list_favorites(db=db, user_id=user_id)


@client_router.get("/game/{game_id}/config", response_model=GameConfigResponse)
async def config_game(game_id: str, jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
                      db: AsyncSession = Depends(get_db_async)):
    """
    Endpoint to get the game configuration.
    """
    org_id = jwt_claims.get("org_id")

    if not org_id:
        raise HTTPException(status_code=401, detail="Unauthorized: Missing org ID in JWT claims.")

    config_project = await services_config_client_game.config_client_game(db=db, org_id=org_id, project_id=game_id)

    if not config_project:
        raise HTTPException(status_code=404, detail="Game not found or could not be updated.")

    return config_project


@client_router.put("/game/{game_id}", response_model=GameConfigResponse)
def update_game(
        game_id: str,
        update_data: GameUpdateRequest,
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
        db: AsyncSession = Depends(get_db_async),
):
    """
    Endpoint to update a game project.
    """
    org_id = jwt_claims.get("org_id")

    if not org_id:
        raise HTTPException(status_code=401, detail="Unauthorized: Missing org ID in JWT claims.")

    updated_project = services_update_client_game.update_client_game(db=db, org_id=org_id, project_id=game_id,
                                                                     update_data=update_data)

    if not updated_project:
        raise HTTPException(status_code=404, detail="Game not found or could not be updated.")

    return updated_project


@client_router.post("/games/{project_id}/add-comment", response_model=ProjectCommentResponse)
def create_comment_endpoint(
        project_id: str,
        req: ProjectCommentCreateRequest,
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
        db: AsyncSession = Depends(get_db_async),
):
    user_id = jwt_claims.get("uid")
    return services_create_comment.create_comment(db, project_id, user_id, req.comment_text)


@client_router.get("/games/{project_id}/comments", response_model=list[ProjectCommentResponse])
def list_comments_endpoint(
        project_id: str,
        db: AsyncSession = Depends(get_db_async),
):
    return services_list_comments.list_comments(db, project_id)


@client_router.put("/comments/{comment_id}", response_model=ProjectCommentResponse)
def update_comment_endpoint(
        comment_id: str,
        updated_data: ProjectCommentUpdateRequest,
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
        db: AsyncSession = Depends(get_db_async),
):
    user_id = jwt_claims.get("uid")
    return services_update_comment.update_comment(db, comment_id, updated_data, user_id)


@client_router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment_endpoint(
        comment_id: str,
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
        db: AsyncSession = Depends(get_db_async),
):
    user_id = jwt_claims.get("uid")
    return services_delete_comment.delete_comment(db, comment_id, user_id)


@client_router.post("/comments/{comment_id}/like", response_model=ProjectCommentResponse)
def like_comment_endpoint(comment_id: str, jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
                          db: AsyncSession = Depends(get_db_async)):
    user_id = jwt_claims.get("uid")
    return services_like_comment.like_comment(db, comment_id, user_id)


@client_router.post("/comments/{comment_id}/dislike", response_model=ProjectCommentResponse)
def dislike_comment_endpoint(comment_id: str, jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
                             db: AsyncSession = Depends(get_db_async)):
    user_id = jwt_claims.get("uid")
    return services_dislike_comment.dislike_comment(db, comment_id, user_id)
