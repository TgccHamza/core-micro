import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Group, Arena, GroupUsers
from app.payloads.response.GroupListClientResponse import ProjectResponse, GroupListUserClientResponse, \
    GroupListArenaClientResponse, GroupListClientResponse
from app.payloads.response.UserResponse import UserResponse
from app.repositories.get_arenas_by_group import get_arenas_by_group
from app.repositories.get_games_by_group import get_games_by_group
from app.repositories.get_groups_by_org import get_groups_by_org
from app.repositories.get_manager_by_group import get_manager_by_group
from app.repositories.get_manager_id_by_group import get_manager_id_by_group
from app.services.user_service import get_user_service

# Set up logging for this module
logger = logging.getLogger(__name__)


# Main function to get groups
async def get_groups(db: AsyncSession, org_id: str) -> List[GroupListClientResponse]:
    db_groups = await get_groups_by_org(org_id, db)
    # Process each group concurrently
    groups = [await process_group(db, db_group) for db_group in db_groups]

    return groups


# Process each individual group
async def process_group(db: AsyncSession, db_group: Group) -> GroupListClientResponse:
    group = GroupListClientResponse(
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
        users = await get_user_service().get_users_by_email(list(id_managers))
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
def process_manager(manager: GroupUsers, users: dict[str, UserResponse]) -> GroupListUserClientResponse:
    user_details = users.get(manager.user_email, None)
    return GroupListUserClientResponse(
        id=manager.id,
        user_id=user_details.user_id if user_details else manager.user_id,
        user_email=user_details.user_email if user_details else manager.user_email,
        first_name=user_details.first_name if user_details else manager.first_name,
        last_name=user_details.last_name if user_details else manager.last_name,
    )


# Process each arena for the group
def process_arena(db_arena: Arena) -> GroupListArenaClientResponse:
    arena = GroupListArenaClientResponse(
        id=db_arena.id,
        name=db_arena.name
    )
    return arena
