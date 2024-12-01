from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models import Group
from app.repositories.get_group_by_id import get_group_by_id

# Set up logging for this module
logger = logging.getLogger(__name__)


async def get_group(db: AsyncSession, group_id: str, org_id: str):
    try:
        # Attempt to fetch the group based on group_id and org_id
        db_group = await get_group_by_id(group_id, db)

        # Log if the group was not found
        if not db_group:
            logger.warning(f"Group with ID {group_id} and organization code {org_id} not found.")
            raise Exception(f"Group with ID {group_id} and organization code {org_id} not found.")

        # Log if the group was not found
        if db_group.organisation_code != org_id:
            logger.warning(f"Group with ID {group_id} and organization code {org_id} not found.")
            raise Exception(f"Group with ID {group_id} and organization code {org_id} not found.")

        return db_group

    except SQLAlchemyError as e:
        # Log any database-related errors
        logger.error(
            f"Database error occurred while fetching group with ID {group_id} and organization code {org_id}: {str(e)}")
        raise Exception("A database error occurred while fetching the group.")

    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Unexpected error occurred while fetching group: {str(e)}")
        raise Exception(f"An unexpected error occurred: {str(e)}")
