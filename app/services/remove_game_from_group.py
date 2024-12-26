from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.exceptions.not_found_exception import NotFoundException
from app.models import Group, GroupProjects
from app.payloads.response.RemoveGameFromGroupResponse import RemoveGameFromGroupResponse


async def remove_game_from_group(group_id: str, game_id: str, organisation_id: str, db: AsyncSession):
    """
    Removes a game from a group if the group exists, belongs to the organization, and the association exists.
    """
    # Validate group existence and ownership
    group = await db.execute(
        select(Group).where(Group.id == str(group_id), Group.organisation_code == organisation_id)
    )
    group = group.scalar_one_or_none()
    if not group:
        raise NotFoundException(
            error=f"Group with ID {group_id} not found or does not belong to the organization"
        )

    # Validate the association exists
    group_project = await db.execute(
        select(GroupProjects).where(GroupProjects.group_id == str(group_id), GroupProjects.project_id == str(game_id))
    )
    group_project = group_project.scalar_one_or_none()
    if not group_project:
        raise NotFoundException(
            error=f"Game with ID {game_id} is not associated with Group {group_id}"
        )

    # Remove the association
    await db.delete(group_project)
    await db.commit()
    # make unique response class for payload not dict
    return RemoveGameFromGroupResponse(
        group_id=str(group_id),
        game_id=str(game_id),
        message="Game successfully removed from the group"
    )
