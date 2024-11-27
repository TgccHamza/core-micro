from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Set, Optional
from app.models import Arena
from app.payloads.response.ArenaListResponseTop import (
    ArenaListResponseTop,
    ArenaListGroupClientResponse,
    ArenaListGroupUserClientResponse,
    ArenaMembers,
)
from app.services.get_arena import get_arena
from app.services.user_service import get_user_service


async def fetch_user_details(user_id: Optional[str], user_email: Optional[str]):
    """
    Fetch user details by ID or email using the UserServiceClient.

    Args:
        user_id (Optional[str]): The user's ID.
        user_email (Optional[str]): The user's email.

    Returns:
        dict: The user details, or None if no match is found.
    """
    user_service = get_user_service()
    user_details = None

    if user_id and user_id != "None":
        user_details = await user_service.get_user_by_id(user_id)

    if not user_details and user_email and user_email != "None":
        user_details = await user_service.get_user_by_email(user_email)

    return user_details


async def map_group_managers(db_group) -> List[ArenaListGroupUserClientResponse]:
    """
    Map managers within a group to their client response.

    Args:
        db_group: The group instance from the database.

    Returns:
        List[ArenaListGroupUserClientResponse]: A list of managers for the group.
    """
    managers = []
    for manager in db_group.managers:
        user_details = await fetch_user_details(manager.user_id, manager.user_email)
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


async def map_arena_groups(db_arena) -> List[ArenaListGroupClientResponse]:
    """
    Map the groups associated with an arena.

    Args:
        db_arena: The arena instance from the database.

    Returns:
        List[ArenaListGroupClientResponse]: A list of groups for the arena.
    """
    groups = []
    for db_group in db_arena.groups:
        managers = await map_group_managers(db_group)
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


async def show_arena(db: Session, arena_id: UUID, org_id: str) -> ArenaListResponseTop:
    """
    Show details of an arena, including its groups and players.

    Args:
        db (Session): The database session.
        arena_id (UUID): The ID of the arena.
        org_id (str): The organization ID.

    Returns:
        ArenaListResponseTop: The response containing arena details.
    """
    db_arena = get_arena(db, arena_id, org_id)
    if not db_arena:
        raise ValueError(f"Arena with ID {arena_id} not found in organization {org_id}")

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
