from uuid import UUID
from typing import List, Set, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Arena
from app.payloads.response.UserResponse import UserResponse
from app.payloads.response.ArenaListResponseTop import (
    ArenaListResponseTop,
    ArenaListGroupClientResponse,
    ArenaListGroupUserClientResponse,
    ArenaMembers,
)
from app.repositories.get_manager_by_group import get_manager_by_group
from app.repositories.get_manager_id_by_arena import get_manager_ids_by_arena
from app.services.get_arena import get_arena
from app.services.user_service import get_user_service
from app.repositories.get_group_by_arena import get_group_by_arena


async def map_group_managers(db_group, db: AsyncSession, users: dict[str, UserResponse]) -> List[ArenaListGroupUserClientResponse]:
    """
    Map managers within a group to their client response.

    Args:
        db_group: The group instance from the database.

    Returns:
        List[ArenaListGroupUserClientResponse]: A list of managers for the group.
    """
    managers = []
    group_managers = await get_manager_by_group(db_group.id, db)
    for manager in group_managers:
        user_details = users.get(manager.user_id, None)
        if user_details:
            managers.append(ArenaListGroupUserClientResponse(
                **user_details,
                picture=manager.picture
            ))
        else:
            managers.append(ArenaListGroupUserClientResponse(
                user_id=manager.user_id,
                user_email=manager.user_email,
                user_name=f"{manager.first_name} {manager.last_name}",
                picture=manager.picture
            ))
    return managers


async def map_arena_groups(db_arena, db: AsyncSession) -> List[ArenaListGroupClientResponse]:
    """
    Map the groups associated with an arena.

    Args:
        db_arena: The arena instance from the database.

    Returns:
        List[ArenaListGroupClientResponse]: A list of groups for the arena.
    """
    groups = []
    arena_groups = await get_group_by_arena(db_arena.id, db)

    for db_group in arena_groups:
        managers = await map_group_managers(db_group, db, users)
        groups.append(ArenaListGroupClientResponse(
            id=db_group.id,
            name=db_group.name,
            managers=managers
        ))
    return groups


async def map_arena_players(db_arena) -> List[ArenaMembers]:
    """
    Map the unique players associated with an arena.

    Args:
        db_arena: The arena instance from the database.

    Returns:
        List[ArenaMembers]: A list of players for the arena.
    """
    dict_players: Set[str] = set()
    players = []

    for session in db_arena.sessions:
        for player in session.players:
            if player.user_email not in dict_players:
                dict_players.add(player.user_email)
                user_details = await fetch_user_details(player.user_id, player.user_email)
                if user_details:
                    players.append(ArenaMembers(
                        **user_details,
                        picture=None
                    ))
                else:
                    players.append(ArenaMembers(
                        user_id=player.user_id,
                        user_email=player.user_email,
                        user_name=player.user_name,
                        picture=None
                    ))
    return players


async def show_arena(db: AsyncSession, arena_id: UUID, org_id: str) -> ArenaListResponseTop:
    """
    Show details of an arena, including its groups and players.

    Args:
        db (Session): The database session.
        arena_id (UUID): The ID of the arena.
        org_id (str): The organization ID.

    Returns:
        ArenaListResponseTop: The response containing arena details.
    """
    db_arena = await get_arena(db, arena_id, org_id)

    group_user_ids = await get_manager_ids_by_arena(db, db_arena.id)
    managers = {}
    if len(group_user_ids) != 0:
        managers = await get_user_service().get_users_by_id(group_user_ids)

    

    # Prepare the response
    arena_response = ArenaListResponseTop(
        id=db_arena.id,
        name=db_arena.name,
        groups=[],
        players=[]
    )

    # Populate groups and players asynchronously
    arena_response.groups = await map_arena_groups(db_arena)
    arena_response.players = await map_arena_players(db_arena)

    return arena_response
