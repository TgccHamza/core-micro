import logging
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import Arena
from fastapi import HTTPException, status

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def validate_arena_id(arena_id: UUID):
    """
    Validates the format of the arena_id.

    Args:
        arena_id (UUID): The arena ID to validate.

    Raises:
        HTTPException: If the arena_id is not a valid UUID format.
    """
    if not isinstance(arena_id, UUID):
        logger.error(f"Invalid arena ID format: {arena_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid arena ID format.")


def get_arena(db: Session, arena_id: UUID, org_id: str) -> Arena:
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
    try:
        # Validate the arena_id format
        validate_arena_id(arena_id)

        # Query the arena from the database
        arena = db.query(Arena).filter(Arena.id == str(arena_id), Arena.organisation_code == org_id).first()

        if not arena:
            logger.warning(f"Arena with ID {arena_id} not found for organization {org_id}.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arena not found")

        logger.info(f"Arena with ID {arena_id} retrieved successfully for organization {org_id}.")
        return arena

    except Exception as e:
        logger.error(f"Error retrieving arena with ID {arena_id} for organization {org_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving arena.")
