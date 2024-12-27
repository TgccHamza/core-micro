import logging
from uuid import UUID
from app.models import Arena
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.validation_error_exception import ValidationErrorException
from app.exceptions.not_found_exception import NotFoundException
from app.repositories.get_arena_by_id_and_org_id import get_arena_by_id_and_org_id

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def validate_arena_id(arena_id: UUID):
    if not isinstance(arena_id, UUID):
        raise ValidationErrorException(error="Invalid arena ID format.")


async def get_arena(db: AsyncSession, arena_id: UUID, org_id: str) -> Arena:
    """
    Fetches a specific Arena by ID and organization ID.

    Args:
        db (Session): The database session.
        arena_id (UUID): The ID of the arena to fetch.
        org_id (str): The organization code associated with the arena.

    Returns:
        Arena: The arena object if found, else raises an exception.

    Raises:
        HTTPException: If the arena is not found.
    """
    # Validate the arena_id format
    validate_arena_id(arena_id)

    # Query the arena from the database
    arena = get_arena_by_id_and_org_id(arena_id, org_id, db)

    if not arena:
        raise NotFoundException(error=f"Arena with ID {arena_id} not found for organization {org_id}.")
    
    return arena
