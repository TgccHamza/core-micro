from sqlalchemy.orm import Session
from typing import List
from app.models import Arena
from sqlalchemy.exc import NoResultFound

from app.payloads.response.ArenaListResponseTop import ArenaListResponseTop, ArenaListGroupClientResponse, \
    ArenaListGroupUserClientResponse, ArenaMembers
from app.services.user_service import get_user_service


async def get_arenas(db: Session, org_id: str) -> List[ArenaListResponseTop]:
    """
    Retrieve a list of arenas for a specific organization.

    Args:
        db (Session): Database session.
        org_id (str): Organization ID.

    Returns:
        List[ArenaListResponseTop]: List of arenas with associated groups and players.
    """
    # Fetch arenas for the given organization
    arenas_data = db.query(Arena).filter(Arena.organisation_code == org_id).all()
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

        # Process groups and players
        arena.groups = await process_groups(db_arena.groups)
        arena.players = await process_players(db_arena.sessions)

        arenas.append(arena)

    return arenas


async def process_groups(db_groups) -> List[ArenaListGroupClientResponse]:
    """
    Process the groups for an arena.

    Args:
        db_groups: Groups associated with an arena.

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

        for manager in db_group.managers:
            user_details = await fetch_user_details(manager.user_id, manager.user_email)

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


async def process_players(db_sessions) -> List[ArenaMembers]:
    """
    Process the players for an arena.

    Args:
        db_sessions: Sessions associated with an arena.

    Returns:
        List[ArenaMembers]: List of processed player data.
    """
    dict_players = set()
    players = []
    for session in db_sessions:
        for player in session.players:
            if player.user_email not in dict_players:
                dict_players.add(player.user_email)
                user_details = await fetch_user_details(player.user_id, player.user_email)

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


async def fetch_user_details(user_id: str, user_email: str):
    """
    Fetch user details using the UserServiceClient.

    Args:
        user_id (str): User ID.
        user_email (str): User email.

    Returns:
        dict: User details if found, else None.
    """
    user_details = None

    if user_id and user_id != 'None':
        user_details = await get_user_service().get_user_by_id(user_id)

    if not user_details and user_email and user_email != 'None':
        user_details = await get_user_service().get_user_by_email(user_email)

    return user_details
