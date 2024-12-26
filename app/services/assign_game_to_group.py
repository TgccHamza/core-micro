from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from uuid import UUID

from app.exceptions.conflict_error_exception import ConflictErrorException
from app.exceptions.not_found_exception import NotFoundException
from app.models import Group, GroupProjects
from app.payloads.response.AssignGameToGroupResponse import AssignGameToGroupResponse


async def assign_game_to_group(group_id: str, game_id: str, organisation_id: str, db: AsyncSession):
    """
    Assigns a game to a group if the group exists and belongs to the organization.
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

    # Check if the association already exists
    existing_association = await db.execute(
        select(GroupProjects).where(GroupProjects.group_id == str(group_id), GroupProjects.project_id == str(game_id))
    )
    if existing_association.scalar_one_or_none():
        raise ConflictErrorException(
            error=f"Game with ID {game_id} is already associated with Group {group_id}"
        )

    # Create the association
    group_project = GroupProjects(group_id=str(group_id), project_id=str(game_id))
    db.add(group_project)
    await db.commit()

    return AssignGameToGroupResponse(
        group_id=str(group_id),
        game_id=str(game_id),
        message=f"Game with ID {game_id} has been successfully associated with Group {group_id}"
    )
