from typing import List, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.models import ArenaSession, Arena, Project

from app.payloads.response.SessionResponse import ArenaGroupResponse, ArenaGroupUserResponse, SessionResponse, \
    ProjectResponse, ArenaResponse, SessionPlayerClientResponse
from app.payloads.response.UserResponse import UserResponse
from app.repositories.get_arena_by_id import get_arena_by_id
from app.repositories.get_game_by_id import get_game_by_id
from app.repositories.get_groups_by_arena import get_groups_by_arena
from app.repositories.get_manager_by_group import get_manager_by_group
from app.repositories.get_manager_id_by_group import get_manager_id_by_group
from app.repositories.get_player_id_by_session import get_player_id_by_session
from app.repositories.get_players_by_session import get_players_by_session
from app.repositories.get_sessions_by_org import get_sessions_by_org
from app.services.user_service import get_user_service


async def get_sessions(db: AsyncSession, org_id: str) -> List[SessionResponse]:
    """
    Retrieves a list of ArenaSession records for a specific organization and maps them to SessionResponse.
    """
    validate_organisation_id(org_id)
    try:
        sessions = await get_sessions_by_org(org_id, db)
        return await map_sessions_to_responses(sessions, db)
    except SQLAlchemyError as e:
        handle_db_error(org_id, e)
    except Exception as e:
        handle_unexpected_error(e)


def validate_organisation_id(org_id: str):
    """
    Validate the organisation ID to ensure it's not empty or None.
    """
    if not org_id:
        raise ValueError("Organisation ID cannot be empty or None")


async def map_sessions_to_responses(sessions_query: Sequence[ArenaSession], db: AsyncSession) -> List[SessionResponse]:
    """
    Map the retrieved ArenaSession records to a list of SessionResponse objects.
    """
    if not sessions_query:
        return []

    sessions = []
    for session in sessions_query:
        session_response = await map_session_to_response(db, session)
        sessions.append(session_response)
    return sessions


async def map_session_to_response(db: AsyncSession, session: ArenaSession) -> SessionResponse:
    """
    Maps a single ArenaSession to a SessionResponse.
    """

    arena = await get_arena_by_id(session.arena_id, db)
    project = await get_game_by_id(session.project_id, session.organisation_code, db)
    players = await get_players_by_session(session.id, db)
    ids = await get_player_id_by_session(session.id, db)
    if len(ids) != 0:
        users = await get_user_service().get_users_by_id(list(ids))
    else:
        users = {}

    return SessionResponse(
        id=session.id,
        super_game_master_mail=session.super_game_master_mail,
        super_game_master_id=session.super_game_master_id,
        arena_id=session.arena_id,
        db_index=session.db_index,
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
    ids = await get_manager_id_by_group(group.id, db)
    if len(ids) != 0:
        users = await get_user_service().get_users_by_id(list(ids))
    else:
        users = {}

    return ArenaGroupResponse(
        id=group.id,
        name=group.name,
        managers=[await _map_group_manager(user, users) for user in managers]
    )


async def _map_group_manager(user, users: dict[str, UserResponse]) -> ArenaGroupUserResponse:
    user_details = users.get(user.user_id, None)

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
    user_details = users.get(user.user_id, None)

    return SessionPlayerClientResponse(
        id=user.id,
        user_id=user_details.user_id if user_details else user.user_id,
        user_email=user_details.user_email if user_details else user.user_email,
        user_name=user_details.user_name if user_details else user.user_name,
        email_status=user.email_status,
        is_game_master=user.is_game_master if user.is_game_master is not None else False
    )


def handle_db_error(org_id: str, error: SQLAlchemyError):
    """
    Handles errors related to database operations.
    """
    raise SQLAlchemyError(f"Error retrieving sessions for organisation {org_id}: {str(error)}")


def handle_unexpected_error(error: Exception):
    """
    Handles any unexpected errors that occur.
    """
    raise Exception(f"Unexpected error occurred while retrieving sessions: {str(error)}")
