from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.exceptions.conflict_error_exception import ConflictErrorException
from app.exceptions.not_found_exception import NotFoundException
from app.models import Group, GroupUsers
from fastapi import HTTPException, status

from app.payloads.response.AssignManagerToGroupByEmailResponse import AssignManagerToGroupByEmailResponse


async def assign_manager_to_group_by_email(
        group_id: str, manager_email: str, organisation_id: str, db: AsyncSession
) -> dict:
    async with db.begin():
        # Validate group existence and organisation ownership
        group_query = await db.execute(select(Group).filter_by(id=str(group_id), organisation_code=organisation_id))
        group = group_query.scalars().first()

        if not group:
            raise NotFoundException(
                error="Group not found or does not belong to your organization"
            )

        # Check if manager already exists
        manager_query = await db.execute(
            select(GroupUsers).filter_by(group_id=str(group_id), user_email=manager_email)
        )
        manager = manager_query.scalars().first()

        if manager:
            raise ConflictErrorException(
                error="Manager is already assigned to this group"
            )

        # Assign manager
        new_manager = GroupUsers(
            group_id=str(group_id),
            user_email=manager_email
        )
        db.add(new_manager)
        await db.commit()

        return AssignManagerToGroupByEmailResponse(
            group_id=str(group_id),
            manager_email=manager_email,
            message="Manager assigned to group successfully"
        )
