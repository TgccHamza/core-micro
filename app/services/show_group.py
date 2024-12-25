import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.models import Group, Arena, GroupUsers
from app.payloads.response.GroupClientResponse import GroupArenaSessionResponse, GroupSessionPlayerClientResponse, \
    GroupUserClientResponse, GroupArenaClientResponse, GroupClientResponse, ProjectResponse
from app.payloads.response.UserResponse import UserResponse
from app.repositories.get_arenas_by_group import get_arenas_by_group
from app.repositories.get_games_by_group import get_games_by_group
from app.repositories.get_manager_by_group import get_manager_by_group
from app.repositories.get_manager_id_by_group import get_manager_id_by_group
from app.services.get_group import get_group
from app.services.user_service import get_user_service

# Set up logging for this module
logger = logging.getLogger(__name__)


async def show_group(db: AsyncSession, group_id: str, org_id: str):
    group = await get_group(db, group_id, org_id)
    return await process_group(db, group)


# # Helper function to get sessions for an arena
# async def fetch_arena_sessions(arena_id: str, db: AsyncSession):
#     return db.query(ArenaSession).filter(ArenaSession.arena_id == arena_id).all()
#
#


# Process each individual group
async def process_group(db: AsyncSession, db_group: Group) -> GroupClientResponse:
    group = GroupClientResponse(
        id=db_group.id,
        name=db_group.name,
        managers=[],
        arenas=[],
        games=[]
    )

    # Fetch manager details concurrently
    managers = await get_manager_by_group(db_group.id, db)
    id_managers = await get_manager_id_by_group(db_group.id, db)
    if len(id_managers) != 0:
        users = await get_user_service().get_users_by_id(list(id_managers))
    else:
        users = {}

    manager_tasks = [
        process_manager(manager, users) for manager in managers
    ]

    group.managers = manager_tasks

    arenas = await get_arenas_by_group(db_group.id, db)
    # Fetch arena details concurrently
    arena_tasks = [
        process_arena(db_arena) for db_arena in arenas
    ]
    group.arenas = arena_tasks

    db_games = await get_games_by_group(db_group.id, db)
    # Process games for the group
    for db_game in db_games:
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
def process_manager(manager: GroupUsers, users: dict[str, UserResponse]) -> GroupUserClientResponse:
    user_details = users.get(manager.user_id, None)
    return GroupUserClientResponse(
        id=manager.id,
        user_id=user_details.user_id if user_details else manager.user_id,
        user_email=user_details.user_email if user_details else manager.user_email,
        first_name=user_details.first_name if user_details else manager.first_name,
        last_name=user_details.last_name if user_details else manager.last_name,
    )


# Process each arena for the group
def process_arena(db_arena: Arena) -> GroupArenaClientResponse:
    arena = GroupArenaClientResponse(
        id=db_arena.id,
        name=db_arena.name
    )
    return arena

# # Process each session for the arena
# async def process_session(db: AsyncSession, db_session: ArenaSession) -> GroupArenaSessionResponse:
#     session = GroupArenaSessionResponse(
#         id=db_session.id,
#         period_type=db_session.period_type,
#         start_time=db_session.start_time,
#         end_time=db_session.end_time,
#         access_status=db_session.access_status,
#         session_status=db_session.session_status,
#         view_access=db_session.view_access,
#         players=[]
#     )
#
#     # Process players concurrently
#     player_tasks = [
#         process_player(player) for player in db_session.players
#     ]
#     session.players = await asyncio.gather(*player_tasks)
#
#     return session
#
#
# # Process each player in the session
# async def process_player(db_player: ArenaSessionPlayers) -> GroupSessionPlayerClientResponse:
#     user_details = await fetch_user_details(db_player.user_id, db_player.user_email)
#
#     if user_details:
#         return GroupSessionPlayerClientResponse(**dict(user_details))
#     else:
#         return GroupSessionPlayerClientResponse(
#             user_id=db_player.user_id,
#             user_email=db_player.user_email,
#             first_name=db_player.user_name,
#             last_name=db_player.user_name
#         )
#
#
# # Helper function to fetch user details
# async def fetch_user_details(user_id: str, user_email: str):
#     if user_id and user_id != 'None':
#         try:
#             return await get_user_service().get_user_by_id(user_id)
#         except Exception as e:
#             logger.error(f"Error fetching user by ID {user_id}: {str(e)}")
#     elif user_email and user_email != 'None':
#         try:
#             return await get_user_service().get_user_by_email(user_email)
#         except Exception as e:
#             logger.error(f"Error fetching user by email {user_email}: {str(e)}")
#     return None
#
