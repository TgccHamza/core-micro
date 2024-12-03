from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Arena
from sqlalchemy.exc import NoResultFound

from app.payloads.response.ArenaListResponseTop import ArenaListResponseTop, ArenaListGroupClientResponse, \
    ArenaListGroupUserClientResponse, ArenaMembers
from app.repositories.get_arenas_by_org import get_arenas_by_org
from app.repositories.get_groups_by_arena import get_groups_by_arena
from app.repositories.get_manager_by_group import get_manager_by_group
from app.repositories.get_manager_id_by_group import get_manager_id_by_group
from app.repositories.get_player_id_by_session import get_player_id_by_session
from app.repositories.get_players_by_session import get_players_by_session
from app.repositories.get_session_by_arena import get_session_by_arena
from app.services.user_service import get_user_service


async def get_arenas(db: AsyncSession, org_id: str) -> List[ArenaListResponseTop]:
    """
    Retrieve a list of arenas for a specific organization.

    Args:
        db (AsyncSession): Database AsyncSession.
        org_id (str): Organization ID.

    Returns:
        List[ArenaListResponseTop]: List of arenas with associated groups and players.
    """
    # Fetch arenas for the given organization

    arenas_data = await get_arenas_by_org(org_id, db)
    if not arenas_data:
        raise NoResultFound(f"No arenas found for organization {org_id}")

    arenas = []
    for db_arena in arenas_data:
        arena = ArenaListResponseTop(
            id=db_arena.id,
            name=db_arena.name,
            groups=[],
            players=[]
        )
        arena_groups = await get_groups_by_arena(db_arena.id, db)
        arena_players = await get_session_by_arena(db_arena.id, db)
        # Process groups and players
        arena.groups = await process_groups(arena_groups, db)
        arena.players = await process_players(arena_players, db)

        arenas.append(arena)

    return arenas


async def process_groups(db_groups, db: AsyncSession) -> List[ArenaListGroupClientResponse]:
    """
    Process the groups for an arena.

    Args:
        db_groups: Groups associated with an arena.
        db: Database.

    Returns:
        List[ArenaListGroupClientResponse]: List of processed group data.
    """
    groups = []
    for db_group in db_groups:
        group = ArenaListGroupClientResponse(
            id=db_group.id,
            name=db_group.name,
            managers=[]
        )
        managers = await get_manager_by_group(db_group.id, db)
        ids = await get_manager_id_by_group(db_group.id, db)
        if len(ids) != 0:
            users = await get_user_service().get_users_by_id(list(ids))
        else:
            users = {}

        for manager in managers:
            user_details = users.get(manager.user_email, None)

            if user_details:
                group.managers.append(ArenaListGroupUserClientResponse(
                    **dict(user_details),
                    picture=manager.picture
                ))
            else:
                group.managers.append(ArenaListGroupUserClientResponse(
                    user_id=manager.user_id,
                    user_email=manager.user_email,
                    user_name=f"{manager.first_name} {manager.last_name}",
                    picture=manager.picture
                ))

        groups.append(group)
    return groups


async def process_players(db_sessions, db: AsyncSession) -> List[ArenaMembers]:
    """
    Process the players for an arena.

    Args:
        db_sessions: Sessions associated with an arena.
        db: Database

    Returns:
        List[ArenaMembers]: List of processed player data.
    """
    dict_players = set()
    players = []
    for session in db_sessions:
        session_players = await get_players_by_session(session.id, db)
        player_ids = await get_player_id_by_session(session.id, db)
        if len(player_ids) != 0:
            users = await get_user_service().get_users_by_email(list(player_ids))
        else:
            users = {}

        for player in session_players:
            if player.user_email not in dict_players:
                dict_players.add(player.user_email)
                user_details = users.get(player.user_email, None)

                if user_details:
                    players.append(ArenaMembers(
                        **dict(user_details),
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
