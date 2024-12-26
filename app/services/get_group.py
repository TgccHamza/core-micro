from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.exceptions.critical_backend_error_exception import CriticalBackendErrorException
from app.exceptions.not_found_exception import NotFoundException
from app.models import Group
from app.repositories.get_group_by_id import get_group_by_id

# Set up logging for this module
logger = logging.getLogger(__name__)


async def get_group(db: AsyncSession, group_id: str, org_id: str):
    # Attempt to fetch the group based on group_id and org_id
    db_group = await get_group_by_id(group_id, db)

    # Log if the group was not found
    if not db_group:
        raise NotFoundException(f"Group with ID {group_id} and organization code {org_id} not found.")

    # Log if the group was not found
    if db_group.organisation_code != org_id:
        raise NotFoundException(f"Group with ID {group_id} and organization code {org_id} not found.")

    return db_group