from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List
from app.payloads.response.GroupByGameResponse import (
    GroupByGameResponse,
    GroupByGameArenaClientResponse,
    GroupByGameUserClientResponse
)
from app.payloads.response.UserResponse import UserResponse
from app.repositories.get_arenas_by_group import get_arenas_by_group
from app.repositories.get_game_by_id import get_game_by_id
from app.repositories.get_groups_by_game import get_groups_by_game
from app.repositories.get_manager_by_group import get_manager_by_group
from app.repositories.get_manager_email_by_game import get_manager_email_by_game
from app.services.user_service import get_user_service


async def groups_by_game(db_session: AsyncSession, game_id: str, org_id: str) -> List[GroupByGameResponse]:
    """
    Fetches groups, arenas, sessions, and their associated players and managers for a game.

    Args:
        db_session (AsyncSession): The database session.
        game_id (str): The game for which to fetch groups.
        org_id (str): The organisation for which to fetch groups.

    Returns:
        List[GroupByGameResponse]: A list of groups with nested details.
    """

    game = await get_game_by_id(game_id=game_id, org_id=org_id, session=db_session)
    if game is None:
        raise Exception("Game not found")

    db_groups = await get_groups_by_game(game_id=game_id, session=db_session)
    groups = []
    emails = await get_manager_email_by_game(game_id=game_id, session=db_session)
    users = await get_user_service().get_users_by_email(list(emails))
    for db_group in db_groups:
        # Build group details
        group = GroupByGameResponse(
            id=db_group.id,
            name=db_group.name,
            managers=[],
            arenas=[]
        )
        # Populate arenas
        group.arenas = await _get_arenas_by_group(db_session, game.id, db_group.id)

        # Populate managers
        group.managers = await _get_managers_by_group(db_session, db_group.id, users)

        groups.append(group)

    return groups


async def _get_arenas_by_group(db_session: AsyncSession, game_id: str, group_id: str) -> List[
    GroupByGameArenaClientResponse]:
    """
    Fetches arenas and their sessions for a given group.

    Args:
        db_session (Session): The database session.
        game_id (int): The game ID to filter sessions.
        db_group: The database group object.

    Returns:
        List[GroupByGameArenaClientResponse]: A list of arenas with nested sessions.
    """
    db_arenas = await get_arenas_by_group(group_id, db_session)
    arenas = []
    for db_arena in db_arenas:
        # Build arena details
        arena = GroupByGameArenaClientResponse(
            id=db_arena.id,
            name=db_arena.name
        )

        arenas.append(arena)

    return arenas


async def _get_managers_by_group(db_session: AsyncSession, group_id: str, users: dict[str, UserResponse]) -> List[
    GroupByGameUserClientResponse]:
    """
    Fetches and enriches managers for a given group with user details.

    Args:
        db_session: The database group object.
        group_id: The group
        users: The users managers

    Returns:
        List[GroupByGameUserClientResponse]: A list of enriched manager responses.
    """
    managers = []
    db_managers = await get_manager_by_group(group_id, db_session)

    for db_manager in db_managers:
        user_details = users.get(db_manager.user_id, None)
        manager_response = GroupByGameUserClientResponse(
            id=str(db_manager.id) if db_manager.id else None,
            user_id=user_details.get("user_id") if user_details else db_manager.user_id,
            user_email=user_details.get("user_email") if user_details else db_manager.user_email,
            first_name=user_details.get("first_name") if user_details else db_manager.first_name,
            last_name=user_details.get("last_name") if user_details else db_manager.last_name,
        )

        managers.append(manager_response)

    return managers
