import asyncio

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models import Group, ArenaSession, ArenaSessionPlayers, Arena
from app.payloads.response.GroupClientResponse import GroupArenaSessionResponse, GroupSessionPlayerClientResponse, \
    GroupUserClientResponse, GroupArenaClientResponse, GroupClientResponse, ProjectResponse
from app.services.get_group import get_group
from app.services.user_service import get_user_service

# Set up logging for this module
logger = logging.getLogger(__name__)


async def show_group(db: Session, group_id: str, org_id: str):
    try:
        group = get_group(db, group_id, org_id)
        return process_group(db, group)
    except Exception as e:
        raise e


# Helper function to get sessions for an arena
async def fetch_arena_sessions(arena_id: str, db: Session):
    return db.query(ArenaSession).filter(ArenaSession.arena_id == arena_id).all()



# Process each individual group
async def process_group(db: Session, db_group: Group) -> GroupClientResponse:
    group = GroupClientResponse(
        id=db_group.id,
        name=db_group.name,
        managers=[],
        arenas=[],
        games=[]
    )

    # Fetch manager details concurrently
    manager_tasks = [
        process_manager(manager, db) for manager in db_group.managers
    ]
    group.managers = await asyncio.gather(*manager_tasks)

    # Fetch arena details concurrently
    arena_tasks = [
        process_arena(db, db_arena) for db_arena in db_group.arenas
    ]
    group.arenas = await asyncio.gather(*arena_tasks)

    # Process games for the group
    for db_game in db_group.games:
        game = ProjectResponse(
            id=db_game.id,
            name=db_game.name,
            description=db_game.description,
            slug=db_game.slug,
            visibility=db_game.visibility,
            activation_status=db_game.activation_status,
            client_id=db_game.client_id,
            client_name=db_game.client_name,
            start_time=db_game.start_time,
            end_time=db_game.end_time
        )
        group.games.append(game)

    return group


# Process each manager for the group
async def process_manager(manager, db: Session) -> GroupUserClientResponse:
    user_details = await fetch_user_details(manager.user_id, manager.user_email)

    if user_details:
        return GroupUserClientResponse(id=manager.id, **dict(user_details))
    else:
        return GroupUserClientResponse(
            id=manager.id,
            user_id=manager.user_id,
            user_email=manager.user_email,
            user_name=f"{manager.first_name} {manager.last_name}",
        )


# Process each arena for the group
async def process_arena(db: Session, db_arena: Arena) -> GroupArenaClientResponse:
    arena = GroupArenaClientResponse(
        id=db_arena.id,
        name=db_arena.name,
        sessions=[]
    )

    # Fetch sessions concurrently for this arena
    arena_sessions = await fetch_arena_sessions(db_arena.id, db)

    # Process each session in the arena
    session_tasks = [process_session(db, db_session) for db_session in arena_sessions]
    arena.sessions = await asyncio.gather(*session_tasks)

    return arena


# Process each session for the arena
async def process_session(db: Session, db_session: ArenaSession) -> GroupArenaSessionResponse:
    session = GroupArenaSessionResponse(
        id=db_session.id,
        period_type=db_session.period_type,
        start_time=db_session.start_time,
        end_time=db_session.end_time,
        access_status=db_session.access_status,
        session_status=db_session.session_status,
        view_access=db_session.view_access,
        players=[]
    )

    # Process players concurrently
    player_tasks = [
        process_player(player) for player in db_session.players
    ]
    session.players = await asyncio.gather(*player_tasks)

    return session


# Process each player in the session
async def process_player(db_player: ArenaSessionPlayers) -> GroupSessionPlayerClientResponse:
    user_details = await fetch_user_details(db_player.user_id, db_player.user_email)

    if user_details:
        return GroupSessionPlayerClientResponse(**dict(user_details))
    else:
        return GroupSessionPlayerClientResponse(
            user_id=db_player.user_id,
            user_email=db_player.user_email,
            first_name=db_player.user_name,
            last_name=db_player.user_name
        )


# Helper function to fetch user details
async def fetch_user_details(user_id: str, user_email: str):
    if user_id and user_id != 'None':
        try:
            return await get_user_service().get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error fetching user by ID {user_id}: {str(e)}")
    elif user_email and user_email != 'None':
        try:
            return await get_user_service().get_user_by_email(user_email)
        except Exception as e:
            logger.error(f"Error fetching user by email {user_email}: {str(e)}")
    return None

