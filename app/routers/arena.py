from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from starlette import status

from app.helpers import get_jwt_claims
from app.middlewares.ClientAuthMiddleware import ClientAuthMiddleware
from app.middlewares.MiddlewareWrapper import middlewareWrapper
from app.models import ArenaSession, Group, GroupUsers, ArenaSessionPlayers, Project
from app.payloads.request.ArenaAssociateRequest import ArenaAssociateRequest
from app.payloads.request.ArenaCreateRequest import ArenaCreateRequest
from app.payloads.request.ArenaDisassociationRequest import ArenaDisassociationRequest
from app.payloads.request.ArenaUpdateRequest import ArenaUpdateRequest
from app.payloads.request.GroupCreateRequest import GroupCreateRequest
from app.payloads.request.GroupInviteManagerRequest import GroupInviteManagerRequest
from app.payloads.request.GroupUpdateRequest import GroupUpdateRequest
from app.payloads.request.InvitePlayerRequest import InvitePlayerRequest
from app.payloads.request.SessionConfigRequest import SessionConfigRequest
from app.payloads.request.SessionCreateRequest import SessionCreateRequest
from app.payloads.response.ArenaListResponseTop import ArenaListResponseTop
from app.payloads.response.ArenaResponseTop import ArenaResponseTop
from app.payloads.response.ArenaShowByGameResponse import ArenaShowByGameResponse
from app.payloads.response.GroupByGameResponse import GroupByGameResponse
from app.payloads.response.GroupClientResponse import GroupClientResponse
from app.payloads.response.InvitePlayerResponse import InvitePlayerResponse
from app.payloads.response.SessionCreateResponse import SessionCreateResponse
from app.payloads.response.SessionResponse import SessionResponse
from app.database import get_db
from uuid import UUID
from sqlalchemy.exc import NoResultFound

from app.services import arena as services_arena
from app.services import config_session as services_config_session
from app.services import delete_session as services_delete_session
from app.services import get_session as services_get_session
from app.services import groups_by_game as services_groups_by_game
from app.services import invite_managers as services_invite_managers
from app.services import invite_players as services_invite_players
from app.services import show_arena_by_game as services_show_arena_by_game
from app.services import update_session as services_update_session

router = APIRouter(
    route_class=middlewareWrapper(middlewares=[ClientAuthMiddleware])
)


# ---------------- Group Routes ----------------

@router.post("/groups", response_model=GroupClientResponse)
def create_group(group: GroupCreateRequest,
                 background_tasks: BackgroundTasks,
                 db: Session = Depends(get_db),
                 jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        return services_arena.create_group(db, group, org_id, background_tasks)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the group: {str(e)}"
        )


@router.get("/groups", response_model=list[GroupClientResponse])
async def list_groups(db: Session = Depends(get_db), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        return await services_arena.get_groups(db, org_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching groups: {str(e)}"
        )


@router.get("/groups/{group_id}", response_model=GroupClientResponse)
def get_group(group_id: str, db: Session = Depends(get_db), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        group = services_arena.get_group(db, group_id, org_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        return group
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the group: {str(e)}"
        )


@router.put("/groups/{group_id}", response_model=GroupClientResponse)
def update_group(group_id: str, group: GroupUpdateRequest, db: Session = Depends(get_db),
                 jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        return services_arena.update_group(db, group_id, group, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Group not found")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the group: {str(e)}"
        )


@router.delete("/groups/{group_id}")
def delete_group(group_id: str, db: Session = Depends(get_db), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        return services_arena.delete_group(db, group_id, org_id)
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
        db: Session = Depends(get_db),
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)
):
    try:
        org_id = jwt_claims.get("org_id")

        group = db.query(Group).filter(Group.id == group_id,
                                       Group.organisation_code == org_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with ID {group_id} not found."
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
def remove_manager(group_manager_id: str, db: Session = Depends(get_db),
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

@router.post("/arenas", response_model=ArenaResponseTop)
def create_arena(arena: ArenaCreateRequest, db: Session = Depends(get_db),
                 jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    return services_arena.create_arena(db, arena, org_id)


@router.get("/arenas", response_model=list[ArenaListResponseTop])
async def list_arenas(db: Session = Depends(get_db), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    return await services_arena.get_arenas(db, org_id)


@router.get("/arenas/{arena_id}", response_model=ArenaListResponseTop)
async def get_arena(arena_id: UUID, db: Session = Depends(get_db),
                    jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    arena = await services_arena.show_arena(db, arena_id, org_id)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")
    return arena


@router.get("/arenas/{arena_id}/game/{game_id}", response_model=ArenaShowByGameResponse)
async def get_arena_by_game(arena_id: UUID, game_id: UUID, db: Session = Depends(get_db),
                            jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    arena = await services_show_arena_by_game.show_arena_by_game(db, arena_id, game_id, org_id)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")
    return arena


@router.put("/arenas/{arena_id}", response_model=ArenaResponseTop)
def update_arena(arena_id: UUID, arena: ArenaUpdateRequest, db: Session = Depends(get_db),
                 jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return services_arena.update_arena(db, arena_id, arena, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena not found")


@router.delete("/arenas/{arena_id}")
def delete_arena(arena_id: UUID, db: Session = Depends(get_db), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return services_arena.delete_arena(db, arena_id, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena not found")


# Associate an arena with an additional group
@router.post("/arenas/{arena_id}/associate", response_model=dict)
def associate_arena(arena_id: UUID, association: ArenaAssociateRequest, db: Session = Depends(get_db),
                    jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return services_arena.associate_arena_with_group(db, arena_id, association.group_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena or Group not found")


# Dissociate an arena from a specific group
@router.post("/arenas/{arena_id}/dissociate", response_model=dict)
def dissociate_arena(arena_id: UUID, dissociation: ArenaDisassociationRequest, db: Session = Depends(get_db),
                     jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return services_arena.dissociate_arena_from_group(db, arena_id, dissociation.group_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena, Group, or Association not found")


# ---------------- Session Routes ----------------

@router.post("/sessions", response_model=SessionCreateResponse)
def create_session(session: SessionCreateRequest, db: Session = Depends(get_db),
                   jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        return services_arena.create_session(db, session, org_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")


@router.post("/sessions/{session_id}/invite-players", response_model=InvitePlayerResponse)
async def invite_players(
        session_id: str,
        background_tasks: BackgroundTasks,
        invite_req: InvitePlayerRequest,
        db: Session = Depends(get_db),
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
    await services_invite_players.invite_players(db, session, invite_req, background_tasks)

    return {"message": "Invitations sent successfully"}


@router.post("/sessions/{session_id}/remove-invitation-players", response_model=InvitePlayerResponse)
async def remove_invited_players(
        session_id: str,
        background_tasks: BackgroundTasks,
        invite_req: InvitePlayerRequest,
        db: Session = Depends(get_db),
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
def list_sessions(db: Session = Depends(get_db), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    return services_arena.get_sessions(db, org_id)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    session = services_get_session.get_session(db, session_id, org_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.put("/sessions/{session_id}/config", response_model=SessionCreateResponse)
def config_session(session_id: str, session: SessionConfigRequest, db: Session = Depends(get_db),
                   jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return services_config_session.config_session(db, session_id, session, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Session not found")


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db),
                   jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return services_delete_session.delete_session(db, session_id, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Session not found")


@router.post("/sessions/player/{session_player_id}/remove")
def remove_player(session_player_id: str, db: Session = Depends(get_db),
                  jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")

    # Perform session validation before processing
    session_user = db.query(ArenaSessionPlayers).filter(ArenaSessionPlayers.id == session_player_id,
                                                        ArenaSessionPlayers.organisation_code == org_id).first()
    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session Player with ID {session_player_id} not found."
        )

    try:
        db.delete(session_user)
        db.commit()
        return {"message": "Player removed from session successfully."}
    except Exception as e:
        db.rollback()  # Rollback in case of an error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while removing the player for this session: {str(e)}"
        )


@router.get("/groups/game/{game_id}", response_model=list[GroupByGameResponse])
async def groups_by_game(
        game_id: str,
        db: Session = Depends(get_db),
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)
):
    org_id = jwt_claims.get("org_id")

    # Perform session validation before processing
    game = db.query(Project).filter(Project.id == game_id,
                                    Project.organisation_code == org_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with ID {game_id} not found."
        )

    return await services_groups_by_game.groups_by_game(db, game)
