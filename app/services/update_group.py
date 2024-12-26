from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.exceptions.not_found_exception import NotFoundException
from app.payloads.request.GroupUpdateRequest import GroupUpdateRequest
from app.payloads.response.GroupLiteClientResponse import GroupLiteClientResponse
from app.services.get_group import get_group

# Set up logging
logger = logging.getLogger(__name__)


async def update_group(db: AsyncSession, group_id: str, group: GroupUpdateRequest, org_id: str):
    try:
        # Fetch the existing group from the database
        db_group = await get_group(db, group_id, org_id)
        if not db_group:
            raise NotFoundException(error=f"Group with ID {group_id} not found in organization {org_id}")

        # Update group details
        db_group.name = group.name

        # Commit the changes to the database
        await db.commit()

        return GroupLiteClientResponse(id=db_group.id, name=db_group.name)
    except Exception as e:
        await db.rollback()
        raise e
