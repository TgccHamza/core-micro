from dbm import error
from typing import Dict, Any, List


from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.exceptions import PlayerNotFoundError, NoResultFoundError
from app.exceptions.not_found_exception import NotFoundException
from app.exceptions.success_exception import SuccessException
from app.exceptions.validation_error_exception import ValidationErrorException
from app.helpers import get_jwt_claims
from app.middlewares.ClientAuthMiddleware import ClientAuthMiddleware
from app.middlewares.MiddlewareWrapper import middlewareWrapper
from app.models import ArenaSession, Group, GroupUsers, ArenaSessionPlayers, Project
from app.payloads.request.ArenaAssociateRequest import ArenaAssociateRequest
from app.payloads.request.ArenaCreateRequest import ArenaCreateRequest
from app.payloads.request.ArenaDisassociationRequest import ArenaDisassociationRequest
from app.payloads.request.ArenaUpdateRequest import ArenaUpdateRequest
from app.payloads.request.AssignModeratorRequest import AssignModeratorRequest
from app.payloads.request.InvitePlayerRequest import InvitePlayerRequest
from app.payloads.request.SessionConfigRequest import SessionConfigRequest
from app.payloads.request.SessionCreateRequest import SessionCreateRequest
from app.payloads.response.ArenaCreateResponse import ArenaCreateResponse
from app.payloads.response.ArenaListResponseTop import ArenaListResponseTop
from app.payloads.response.ArenaResponseTop import ArenaResponseTop
from app.payloads.response.ArenaShowByGameResponse import ArenaShowByGameResponse
from app.payloads.response.GroupByGameResponse import GroupByGameResponse
from app.payloads.response.InvitePlayerResponse import InvitePlayerResponse
from app.payloads.response.SessionCreateResponse import SessionCreateResponse
from app.payloads.response.SessionResponse import SessionResponse
from app.database import get_db_async
from uuid import UUID
from sqlalchemy.exc import NoResultFound

from app.payloads.response.SuccessResponse import SuccessResponse
from app.services import create_arena as services_create_arena
from app.services import get_arenas as services_get_arenas
from app.services import show_arena as services_show_arena
from app.services import update_arena as services_update_arena
from app.services import delete_arena as services_delete_arena
from app.services import associate_arena_with_group as services_associate_arena_with_group
from app.services import dissociate_arena_from_group as services_dissociate_arena_from_group
from app.services import remove_player_from_session as services_remove_player_from_session
from app.services import assign_moderator as services_assign_moderator
from app.services import invite_players as services_invite_players
from app.services import show_arena_by_game as services_show_arena_by_game
from app.services import get_sessions as services_get_sessions
from app.services import create_session as services_create_session
from app.services import config_session as services_config_session
from app.services import delete_session as services_delete_session
from app.services import show_session as services_show_session
from app.services import groups_by_game as services_groups_by_game

import logging


logger = logging.getLogger(__name__)

router = APIRouter(
    route_class=middlewareWrapper(middlewares=[ClientAuthMiddleware])
)



# ---------------- Arena Routes ----------------

@router.post("/arenas", response_model=ArenaCreateResponse)
async def create_arena(arena: ArenaCreateRequest, db: AsyncSession = Depends(get_db_async),
                       jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    """
    Create a new arena.

    Args:
        arena (ArenaCreateRequest): The request body containing the arena details.
        db (AsyncSession): The database session dependency.
        jwt_claims (Dict[Any, Any]): The JWT claims dependency.

    Returns:
        SuccessResponse[ArenaCreateResponse]: The response containing the created arena details.
    """
    org_id = jwt_claims.get("org_id")
    response = await services_create_arena.create_arena(db, arena, org_id)
    return SuccessResponse[ArenaCreateResponse](data=response)


@router.get("/arenas", response_model=SuccessResponse[List[ArenaListResponseTop]])
async def list_arenas(db: AsyncSession = Depends(get_db_async), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    """
    Endpoint to list arenas.

    This endpoint retrieves a list of arenas associated with the organization ID
    extracted from the JWT claims.

    Args:
        db (AsyncSession): The database session dependency.
        jwt_claims (Dict[Any, Any]): The JWT claims dependency containing user information.

    Returns:
        SuccessResponse[List[ArenaListResponseTop]]: A success response containing a list of arenas.
    """

    org_id = jwt_claims.get("org_id")
    response = await services_get_arenas.get_arenas(db, org_id)
    return SuccessResponse[List[ArenaListResponseTop]](data=response)


@router.get("/arenas/{arena_id}", response_model=SuccessResponse[ArenaResponseTop])
async def get_arena(arena_id: UUID, db: AsyncSession = Depends(get_db_async),
                    jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    arena = await services_show_arena.show_arena(db, arena_id, org_id)
    return arena


@router.get("/arenas/{arena_id}/game/{game_id}", response_model=ArenaShowByGameResponse)
async def get_arena_by_game(arena_id: UUID, game_id: UUID, db: AsyncSession = Depends(get_db_async),
                            jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    arena = await services_show_arena_by_game.show_arena_by_game(db, arena_id, game_id, org_id)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")
    return arena


@router.put("/arenas/{arena_id}", response_model=ArenaCreateResponse)
async def update_arena(arena_id: UUID, arena: ArenaUpdateRequest, db: AsyncSession = Depends(get_db_async),
                       jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return services_update_arena.update_arena(db, arena_id, arena, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena not found")


@router.delete("/arenas/{arena_id}")
def delete_arena(arena_id: UUID, db: AsyncSession = Depends(get_db_async),
                 jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return services_delete_arena.delete_arena(db, arena_id, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena not found")


# Associate an arena with an additional group
@router.post("/arenas/{arena_id}/associate", response_model=dict)
def associate_arena(arena_id: UUID, association: ArenaAssociateRequest, db: AsyncSession = Depends(get_db_async),
                    jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return services_associate_arena_with_group.associate_arena_with_group(db, arena_id, association.group_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena or Group not found")


# Dissociate an arena from a specific group
@router.post("/arenas/{arena_id}/dissociate", response_model=dict)
def dissociate_arena(arena_id: UUID, dissociation: ArenaDisassociationRequest, db: AsyncSession = Depends(get_db_async),
                     jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return services_dissociate_arena_from_group.dissociate_arena_from_group(db, arena_id, dissociation.group_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena, Group, or Association not found")

