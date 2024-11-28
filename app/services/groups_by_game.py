import asyncio

from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import ArenaSession, Project, GroupUsers, ArenaSessionPlayers
from app.payloads.response.GroupByGameResponse import (
    GroupByGameResponse,
    GroupByGameArenaClientResponse,
    GroupByGameArenaSessionResponse,
    GroupByGameSessionPlayerClientResponse,
    GroupByGameUserClientResponse
)
from app.payloads.response.UserResponse import UserResponse
from app.services.user_service import get_user_service


async def groups_by_game(db: Session, game: Project) -> List[GroupByGameResponse]:
    """
    Fetches groups, arenas, sessions, and their associated players and managers for a game.

    Args:
        db (Session): The database session.
        game (Project): The game for which to fetch groups.

    Returns:
        List[GroupByGameResponse]: A list of groups with nested details.
    """
    groups = []

    for db_group in game.groups:
        # Build group details
        group = GroupByGameResponse(
            id=db_group.id,
            name=db_group.name,
            managers=[],
            arenas=[]
        )

        # Populate arenas
        group.arenas = await _get_arenas_by_group(db, game.id, db_group)

        # Populate managers
        group.managers = await _get_managers_by_group(db_group)

        groups.append(group)

    return groups


async def _get_arenas_by_group(db: Session, game_id: str, db_group) -> List[GroupByGameArenaClientResponse]:
    """
    Fetches arenas and their sessions for a given group.

    Args:
        db (Session): The database session.
        game_id (int): The game ID to filter sessions.
        db_group: The database group object.

    Returns:
        List[GroupByGameArenaClientResponse]: A list of arenas with nested sessions.
    """
    arenas = []

    for db_arena in db_group.arenas:
        # Build arena details
        arena = GroupByGameArenaClientResponse(
            id=db_arena.id,
            name=db_arena.name,
            sessions=[]
        )

        # Fetch sessions
        arena_sessions = db.query(ArenaSession).filter(
            ArenaSession.project_id == game_id,
            ArenaSession.arena_id == db_arena.id
        )

        # Populate sessions
        arena.sessions = await _get_sessions_by_arena(arena_sessions)

        arenas.append(arena)

    return arenas


async def _get_sessions_by_arena(arena_sessions) -> List[GroupByGameArenaSessionResponse]:
    """
    Fetches sessions and their associated players for a given arena.

    Args:
        arena_sessions: Queryset of arena sessions.

    Returns:
        List[GroupByGameArenaSessionResponse]: A list of sessions with nested players.
    """
    sessions = []

    for db_session in arena_sessions:
        # Build session details
        session = GroupByGameArenaSessionResponse(
            id=db_session.id,
            period_type=db_session.period_type,
            start_time=db_session.start_time,
            end_time=db_session.end_time,
            access_status=db_session.access_status,
            session_status=db_session.session_status,
            view_access=db_session.view_access,
            players=[]
        )

        # Populate players
        session.players = await _get_players_by_session(db_session)

        sessions.append(session)

    return sessions


async def _get_players_by_session(db_session) -> List[GroupByGameSessionPlayerClientResponse]:
    """
    Fetches players for a given session.

    Args:
        db_session: The session object containing players.

    Returns:
        List[GroupByGameSessionPlayerClientResponse]: A list of player responses.
    """
    players = []

    players_details = await _fetch_users_concurrently(db_session.players)

    for db_player, user_details in zip(db_session.players, players_details):
        # Build player details
        if user_details:
            player = GroupByGameSessionPlayerClientResponse(
                **dict(user_details)
            )
        else:
            player = GroupByGameSessionPlayerClientResponse(
                user_id=str(db_player.user_id) if db_player.user_id else None,
                email=db_player.user_email,
                first_name=db_player.user_name,
                last_name=db_player.user_name
            )

        players.append(player)

    return players


async def _fetch_user_details(user_id: Optional[str], user_email: Optional[str]) -> Optional[dict]:
    """
    Fetches user details by ID or email using the UserServiceClient.

    Args:
        user_id (Optional[str]): The user ID.
        user_email (Optional[str]): The user email.

    Returns:
        Optional[dict]: A dictionary of user details if found, otherwise None.
    """
    user_service = get_user_service()

    if user_id:
        user_details = await user_service.get_user_by_id(user_id)
        if user_details:
            return user_details

    if user_email:
        return await user_service.get_user_by_email(user_email)

    return None


async def _fetch_users_concurrently(users: List[ArenaSessionPlayers | GroupUsers]) -> List[Optional[UserResponse]]:
    """
    Fetch user details concurrently for multiple players.

    Args:
        users (List[ArenaSessionPlayers]): List of players to fetch details for

    Returns:
        List[Optional[UserResponse]]: List of user details
    """
    # Create tasks for concurrent user detail fetching
    fetch_tasks = [
        _fetch_user_details(user.user_id, user.user_email)
        for user in users
    ]

    # Wait for all tasks to complete
    return await asyncio.gather(*fetch_tasks)


async def _get_managers_by_group(db_group) -> List[GroupByGameUserClientResponse]:
    """
    Fetches and enriches managers for a given group with user details.

    Args:
        db_group: The database group object.

    Returns:
        List[GroupByGameUserClientResponse]: A list of enriched manager responses.
    """
    managers = []

    manager_details = await _fetch_users_concurrently(db_group.managers)

    for db_manager, user_details in zip(db_group.managers, manager_details):
        manager_response = GroupByGameUserClientResponse(
            id=str(db_manager.id) if db_manager.id else None,
            user_id=user_details.get("user_id") if user_details else db_manager.user_id,
            user_email=user_details.get("user_email") if user_details else db_manager.user_email,
            first_name=user_details.get("first_name") if user_details else db_manager.first_name,
            last_name=user_details.get("last_name") if user_details else db_manager.last_name,
        )

        managers.append(manager_response)

    return managers
