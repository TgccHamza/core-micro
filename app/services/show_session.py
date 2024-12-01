import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.models import ArenaSession, Arena, Project

from app.payloads.response.SessionResponse import SessionPlayerClientResponse, ArenaGroupUserResponse, ArenaResponse, \
    ArenaGroupResponse, ProjectResponse, SessionResponse
from app.payloads.response.UserResponse import UserResponse
from app.repositories.get_game_by_id import get_game_by_id
from app.repositories.get_arena_by_id import get_arena_by_id
from app.repositories.get_groups_by_arena import get_groups_by_arena
from app.repositories.get_manager_by_group import get_manager_by_group
from app.repositories.get_manager_email_by_group import get_manager_email_by_group
from app.repositories.get_player_email_by_session import get_player_email_by_session
from app.repositories.get_players_by_session import get_players_by_session
from app.services.get_session import get_session
from app.services.user_service import get_user_service

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def show_session(db: AsyncSession, session_id: str, org_id: str) -> SessionResponse:
    try:

        session = await get_session(db, session_id, org_id)
        return await map_session_to_response(db, session)

    except SQLAlchemyError as e:
        # Handle any database-related errors
        logger.error(
            f"Database error occurred while retrieving session {session_id} for organization {org_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the session."
        )

    except Exception as e:
        # Handle any other unexpected errors
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the session."
        )


async def map_session_to_response(db: AsyncSession, session: ArenaSession) -> SessionResponse:
    """
    Maps a single ArenaSession to a SessionResponse.
    """
    arena = await get_arena_by_id(session.arena_id, db)
    project = await get_game_by_id(session.project_id, session.organisation_code, db)
    players = await get_players_by_session(session.id, db)
    emails = await get_player_email_by_session(session.id, db)
    if len(emails) != 0:
        users = await get_user_service().get_users_by_email(list(emails))
    else:
        users = {}
    return SessionResponse(
        id=session.id,
        super_game_master_mail=session.super_game_master_mail,
        arena_id=session.arena_id,
        project_id=session.project_id,
        period_type=session.period_type,
        start_time=session.start_time,
        end_time=session.end_time,
        access_status=session.access_status,
        session_status=session.session_status,
        view_access=session.view_access,
        project=map_project(project),
        arena=await _map_arena(arena, db),
        players=await _map_players(players, users)
    )


def map_project(project: Project) -> ProjectResponse | None:
    """
    Maps the Project model to ProjectResponse.
    """
    if not project:
        return None

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        db_index=project.db_index,
        slug=project.slug,
        visibility=project.visibility,
        activation_status=project.activation_status,
        client_id=project.client_id,
        client_name=project.client_name,
        start_time=project.start_time,
        end_time=project.end_time
    )


async def _map_arena(arena: Arena, db: AsyncSession) -> ArenaResponse | None:
    """
    Maps the Arena model to ArenaResponse.
    """
    if not arena:
        return None

    groups = await get_groups_by_arena(arena.id, db)
    return ArenaResponse(
        id=arena.id,
        name=arena.name,
        groups=[await _map_arena_group(group, db) for group in groups]
    )


async def _map_arena_group(group, db: AsyncSession) -> ArenaGroupResponse:
    """
    Maps ArenaGroup model to ArenaGroupResponse.
    """
    managers = await get_manager_by_group(group.id, db)
    emails = await get_manager_email_by_group(group.id, db)
    if len(emails) != 0:
        users = await get_user_service().get_users_by_email(list(emails))
    else:
        users = {}

    return ArenaGroupResponse(
        id=group.id,
        name=group.name,
        managers=[await _map_group_manager(user, users) for user in managers]
    )


async def _map_group_manager(user, users: dict[str, UserResponse]) -> ArenaGroupUserResponse:
    user_details = users.get(user.user_email, None)

    """
    Maps ArenaGroup model to ArenaGroupResponse.
    """
    return ArenaGroupUserResponse(
        user_id=user_details.user_id if user_details else user.user_id,
        email=user_details.user_email if user_details else user.user_email,
        first_name=user_details.first_name if user_details else user.first_name,
        last_name=user_details.last_name if user_details else user.last_name
    )


async def _map_players(players, users) -> List[SessionPlayerClientResponse]:
    """
    Maps players in the session to SessionPlayerClientResponse.
    """
    return [
        await _map_player(player, users)
        for player in players
    ]


async def _map_player(user, users) -> SessionPlayerClientResponse:
    user_details = users.get(user.user_email, None)

    return SessionPlayerClientResponse(
        id=user.id,
        user_id=user_details.user_id if user_details else user.user_id,
        user_email=user_details.user_email if user_details else user.user_email,
        user_name=user_details.user_name if user_details else user.user_name,
        email_status=user.email_status
    )