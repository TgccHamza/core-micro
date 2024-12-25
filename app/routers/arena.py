from dbm import error
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.exceptions import PlayerNotFoundError, NoResultFoundError
from app.exceptions.not_found_exception import NotFoundException
from app.exceptions.success_exception import SuccessException
from app.helpers import get_jwt_claims
from app.middlewares.ClientAuthMiddleware import ClientAuthMiddleware
from app.middlewares.MiddlewareWrapper import middlewareWrapper
from app.models import ArenaSession, Group, GroupUsers, ArenaSessionPlayers, Project
from app.payloads.request.ArenaAssociateRequest import ArenaAssociateRequest
from app.payloads.request.ArenaCreateRequest import ArenaCreateRequest
from app.payloads.request.ArenaDisassociationRequest import ArenaDisassociationRequest
from app.payloads.request.ArenaUpdateRequest import ArenaUpdateRequest
from app.payloads.request.AssignModeratorRequest import AssignModeratorRequest
from app.payloads.request.GroupCreateRequest import GroupCreateRequest
from app.payloads.request.GroupInviteManagerRequest import GroupInviteManagerRequest
from app.payloads.request.GroupUpdateRequest import GroupUpdateRequest
from app.payloads.request.InvitePlayerRequest import InvitePlayerRequest
from app.payloads.request.SessionConfigRequest import SessionConfigRequest
from app.payloads.request.SessionCreateRequest import SessionCreateRequest
from app.payloads.response.ArenaCreateResponse import ArenaCreateResponse
from app.payloads.response.ArenaListResponseTop import ArenaListResponseTop
from app.payloads.response.ArenaResponseTop import ArenaResponseTop
from app.payloads.response.ArenaShowByGameResponse import ArenaShowByGameResponse
from app.payloads.response.GroupByGameResponse import GroupByGameResponse
from app.payloads.response.GroupClientResponse import GroupClientResponse
from app.payloads.response.GroupCreateClientResponse import GroupCreateClientResponse
from app.payloads.response.GroupListClientResponse import GroupListClientResponse
from app.payloads.response.InvitePlayerResponse import InvitePlayerResponse
from app.payloads.response.SessionCreateResponse import SessionCreateResponse
from app.payloads.response.SessionResponse import SessionResponse
from app.database import get_db_async
from uuid import UUID
from sqlalchemy.exc import NoResultFound

from app.payloads.response.SuccessResponse import SuccessResponse
from app.repositories.get_group_by_id import get_group_by_id
from app.repositories.get_session_by_id import get_session_by_id
from app.services import config_session as services_config_session
from app.services import delete_session as services_delete_session
from app.services import show_session as services_show_session
from app.services import groups_by_game as services_groups_by_game
from app.services import invite_managers as services_invite_managers
from app.services import invite_players as services_invite_players
from app.services import show_arena_by_game as services_show_arena_by_game
from app.services import get_sessions as services_get_sessions
from app.services import create_session as services_create_session
from app.services import create_group as services_create_group
from app.services import get_groups as services_get_groups
from app.services import update_group as services_update_group
from app.services import delete_group as services_delete_group
from app.services import create_arena as services_create_arena
from app.services import get_arenas as services_get_arenas
from app.services import show_arena as services_show_arena
from app.services import update_arena as services_update_arena
from app.services import delete_arena as services_delete_arena
from app.services import associate_arena_with_group as services_associate_arena_with_group
from app.services import dissociate_arena_from_group as services_dissociate_arena_from_group
from app.services import remove_player_from_session as services_remove_player_from_session
from app.services import show_group as services_show_group
from app.services import assign_moderator as services_assign_moderator

import logging

from app.services.assign_game_to_group import assign_game_to_group
from app.services.assign_manager_to_group_by_email import assign_manager_to_group_by_email
from app.services.remove_game_from_group import remove_game_from_group
from app.services.remove_manager_from_group_by_email import remove_manager_from_group_by_email

logger = logging.getLogger(__name__)

router = APIRouter(
    route_class=middlewareWrapper(middlewares=[ClientAuthMiddleware])
)


# ---------------- Group Routes ----------------

@router.post("/groups", response_model=SuccessResponse[GroupCreateClientResponse])
async def create_group(group: GroupCreateRequest,
                       background_tasks: BackgroundTasks,
                       db: AsyncSession = Depends(get_db_async),
                       jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    response = await services_create_group.create_group(db, group, org_id, background_tasks)
    return SuccessResponse[GroupCreateClientResponse](data=response)


@router.get("/groups", response_model=SuccessResponse[List[GroupListClientResponse]])
async def list_groups(db: AsyncSession = Depends(get_db_async), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    response = await services_get_groups.get_groups(db, org_id)
    data = SuccessResponse[List[GroupListClientResponse]](data=response)
    return data


@router.get("/groups/{group_id}", response_model=SuccessResponse[GroupClientResponse])
async def get_group(group_id: str, db: AsyncSession = Depends(get_db_async),
                    jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    group = await services_show_group.show_group(db, group_id, org_id)
    if not group:
        raise NotFoundException(error="Group not found")
    return SuccessResponse[GroupClientResponse](data=group)


@router.post("/groups/{group_id}/assign-game/{game_id}")
async def associate_project_to_group(group_id: UUID, game_id: UUID, db: AsyncSession = Depends(get_db_async),
                                     jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        # make the service code here

        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization ID missing from JWT claims"
            )

        return await assign_game_to_group(group_id=str(group_id), game_id=str(game_id), organisation_id=org_id, db=db)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the group: {str(e)}"
        )


@router.delete("/groups/{group_id}/remove-game/{game_id}")
async def disassociate_project_in_group(group_id: UUID, game_id: UUID, db: AsyncSession = Depends(get_db_async),
                                        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization ID missing from JWT claims"
            )

        return await remove_game_from_group(group_id=str(group_id), game_id=str(game_id), organisation_id=org_id, db=db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the group: {str(e)}"
        )


@router.post("/groups/{group_id}/assign-manager-by-email/{manager_email}")
async def associate_manager_to_group(
        group_id: UUID,
        manager_email: str,
        db: AsyncSession = Depends(get_db_async),
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)
):
    try:
        org_id = jwt_claims.get("org_id")
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization ID missing from JWT claims"
            )
        return await assign_manager_to_group_by_email(group_id=str(group_id), manager_email=manager_email,
                                                      organisation_id=org_id, db=db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while assigning the manager: {str(e)}"
        )


@router.delete("/groups/{group_id}/remove-manager-by-email/{manager_email}")
async def disassociate_manager_from_group(
        group_id: UUID,
        manager_email: str,
        db: AsyncSession = Depends(get_db_async),
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)
):
    try:
        org_id = jwt_claims.get("org_id")
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization ID missing from JWT claims"
            )
        return await remove_manager_from_group_by_email(group_id=str(group_id), manager_email=manager_email,
                                                        organisation_id=org_id, db=db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while removing the manager: {str(e)}"
        )


@router.put("/groups/{group_id}", response_model=GroupCreateClientResponse)
async def update_group(group_id: str, group: GroupUpdateRequest, db: AsyncSession = Depends(get_db_async),
                       jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        return await services_update_group.update_group(db, group_id, group, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Group not found")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the group: {str(e)}"
        )


@router.delete("/groups/{group_id}")
async def delete_group(group_id: str, db: AsyncSession = Depends(get_db_async),
                       jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        return await services_delete_group.delete_group(db, group_id, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Group not found")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the group: {str(e)}"
        )


@router.post("/groups/{group_id}/invite-managers")
async def invite_manager(
        group_id: str,
        background_tasks: BackgroundTasks,
        invite_req: GroupInviteManagerRequest,
        db: AsyncSession = Depends(get_db_async),
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)
):
    try:
        org_id = jwt_claims.get("org_id")

        group = await get_group_by_id(group_id, db)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with ID {group_id} not found."
            )

        if group.organisation_code != org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organisation not allowed."
            )

        await services_invite_managers.invite_managers(db, group, invite_req.managers, background_tasks)
        return {"message": "Invitations sent successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while inviting managers: {str(e)}"
        )


@router.post("/groups/manager/{group_manager_id}/remove")
def remove_manager(group_manager_id: str, db: AsyncSession = Depends(get_db_async),
                   jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")

        group_user = db.query(GroupUsers).filter(GroupUsers.id == group_manager_id).first()
        if not group_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"GroupUser with ID {group_manager_id} not found."
            )

        if not group_user.group or group_user.group.organisation_code != org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found."
            )

        db.delete(group_user)
        db.commit()
        return {"message": "Group manager removed successfully."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()  # Rollback in case of an error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while removing the group manager: {str(e)}"
        )


# ---------------- Arena Routes ----------------

@router.post("/arenas", response_model=ArenaCreateResponse)
async def create_arena(arena: ArenaCreateRequest, db: AsyncSession = Depends(get_db_async),
                       jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    return await services_create_arena.create_arena(db, arena, org_id)


@router.get("/arenas", response_model=list[ArenaListResponseTop])
async def list_arenas(db: AsyncSession = Depends(get_db_async), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    return await services_get_arenas.get_arenas(db, org_id)


@router.get("/arenas/{arena_id}", response_model=ArenaListResponseTop)
async def get_arena(arena_id: UUID, db: AsyncSession = Depends(get_db_async),
                    jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    arena = await services_show_arena.show_arena(db, arena_id, org_id)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")
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


# ---------------- Session Routes ----------------

@router.post("/sessions", response_model=SessionCreateResponse)
async def create_session(session: SessionCreateRequest, db: AsyncSession = Depends(get_db_async),
                         jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        return await services_create_session.create_session(db, session, org_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")


@router.post("/sessions/{session_id}/invite-players", response_model=InvitePlayerResponse)
async def invite_players(
        session_id: str,
        background_tasks: BackgroundTasks,
        invite_req: InvitePlayerRequest,
        db: AsyncSession = Depends(get_db_async),
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)
):
    org_id = jwt_claims.get("org_id")

    # Perform session validation before processing
    session = await get_session_by_id(session_id, org_id, db)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Arena session with ID {session_id} not found."
        )

    # Call the service to handle player invitations
    await services_invite_players.invite_players(db, session, invite_req, background_tasks)

    return {"message": "Invitations sent successfully"}


@router.post("/sessions/{session_id}/remove-invitation-players", response_model=InvitePlayerResponse)
async def remove_invited_players(
        session_id: str,
        background_tasks: BackgroundTasks,
        invite_req: InvitePlayerRequest,
        db: AsyncSession = Depends(get_db_async),
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)
):
    org_id = jwt_claims.get("org_id")

    # Perform session validation before processing
    session = db.query(ArenaSession).filter(ArenaSession.id == session_id,
                                            ArenaSession.organisation_code == org_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Arena session with ID {session_id} not found."
        )

    # Call the service to handle player invitations
    # await service.remove_invited_players(db, session, invite_req, background_tasks)

    return {"message": "Invitations removed successfully"}


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db_async), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        sessions = await services_get_sessions.get_sessions(db, org_id)
        return sessions
    except Exception as e:
        # General error handling for unexpected issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db_async),
                      jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        session = await services_show_session.show_session(db, session_id, org_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        # General error handling for unexpected issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while get the session: {str(e)}"
        )


@router.put("/sessions/{session_id}/config", response_model=SessionCreateResponse)
def config_session(session_id: str, session: SessionConfigRequest, db: AsyncSession = Depends(get_db_async),
                   jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        try:
            return services_config_session.config_session(db, session_id, session, org_id)
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Session not found")

    except Exception as e:
        # General error handling for unexpected issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while config the session: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db_async),
                         jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    """
    Deletes a session by its ID. Ensures the session exists and belongs to the correct organization.
    """
    org_id = jwt_claims.get("org_id")

    try:
        # Delegate the session deletion logic to the service layer
        await services_delete_session.delete_session(db, session_id, org_id)
        return {"message": "Session deleted successfully."}

    except NoResultFoundError:
        # Specific exception when the session is not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found."
        )
    except Exception as e:
        # General error handling for unexpected issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the session: {str(e)}"
        )


@router.post("/sessions/player/{session_player_id}/remove")
async def remove_player(session_player_id: str, db: AsyncSession = Depends(get_db_async),
                        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    """
    Removes a player from the specified session.
    Ensures the player exists and belongs to the correct organization.
    """
    org_id = jwt_claims.get("org_id")

    try:
        # Delegate session validation and removal to the service layer
        await services_remove_player_from_session.remove_player_from_session(db, session_player_id, org_id)
        return {"message": "Player removed from session successfully."}

    except PlayerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session Player with ID {session_player_id} not found."
        )
    except Exception as e:
        # Handle any unforeseen errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while removing the player: {str(e)}"
        )


@router.get("/groups/game/{game_id}", response_model=List[GroupByGameResponse])
async def groups_by_game(
        game_id: str,
        db: AsyncSession = Depends(get_db_async),
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)
):
    """
    Endpoint to retrieve groups by game.

    This endpoint fetches the groups related to a specific game, ensuring that the game
    belongs to the organization of the current user. It calls the `groups_by_game`
    service to retrieve the group details.

    Parameters:
    - game_id (str): The ID of the game.
    - db (Session): The database session, injected through dependency.
    - jwt_claims (Dict): The JWT claims containing organization info.

    Returns:
    - List[GroupByGameResponse]: A list of groups associated with the game.

    Raises:
    - HTTPException: If the game is not found or does not belong to the user's organization.
    """
    try:
        org_id = jwt_claims.get("org_id")

        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization ID missing in JWT claims."
            )

        # Call the service to get groups related to the game
        groups = await services_groups_by_game.groups_by_game(db, game_id, org_id)

        if not groups:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No groups found for the game with ID {game_id}."
            )

        return groups

    except Exception as e:
        # Log the error (you can use a logger like 'logging' or any other framework)
        logger.error(f"Error in groups_by_game: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request {e}"
        )


@router.post("/sessions/{session_id}/assign-moderator", response_model=dict)
async def assign_moderator(session_id: str, background_tasks: BackgroundTasks, req: AssignModeratorRequest,
                           db: AsyncSession = Depends(get_db_async),
                           jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")

    # Call the service to handle player invitations
    await services_assign_moderator.assign_moderator(db, session_id, org_id, req.email, background_tasks)

    return {"message": "Invitations sent successfully"}
