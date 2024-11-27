import logging
import re
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app.models import ArenaSession
from uuid import UUID

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def is_valid_uuid(value: str) -> bool:
    """
    Validates if the given value is a valid UUID format.

    Args:
        value (str): The value to validate.

    Returns:
        bool: True if the value is a valid UUID, False otherwise.
    """
    try:
        # Attempt to parse the value as a UUID
        UUID(value)
        return True
    except ValueError:
        return False


def is_valid_org_code(value: str) -> bool:
    """
    Validates the format of the organization code.

    Args:
        value (str): The organization code to validate.

    Returns:
        bool: True if the organization code is valid, False otherwise.
    """
    # Assuming the org code should be alphanumeric and non-empty
    return bool(value) and re.match(r"^[A-Za-z0-9_-]+$", value)


def get_session(db: Session, session_id: str, org_id: str) -> ArenaSession:
    """
    Retrieves a session by its ID and associated organization code, with input validation.

    Args:
        db (Session): Database session for querying.
        session_id (str): The ID of the session to retrieve.
        org_id (str): The organization code associated with the session.

    Returns:
        ArenaSession: The session object if found.

    Raises:
        HTTPException: If the session is not found, raises a 404 error.
        SQLAlchemyError: If there is an issue with the database query, raises a 500 error.
    """
    # Input Validation
    if not session_id or not is_valid_uuid(session_id):
        logger.warning(f"Invalid session ID format: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format."
        )

    if not org_id or not is_valid_org_code(org_id):
        logger.warning(f"Invalid organization code format: {org_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid organization code format."
        )

    try:
        # Query the session based on session_id and org_id
        session = db.query(ArenaSession).filter(
            ArenaSession.id == session_id,
            ArenaSession.organisation_code == org_id
        ).first()

        if not session:
            logger.warning(f"Session with ID {session_id} not found for organization {org_id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found for the provided organization code."
            )

        logger.info(f"Successfully retrieved session with ID {session_id} for organization {org_id}.")
        return session

    except SQLAlchemyError as e:
        # Handle any database-related errors
        logger.error(
            f"Database error occurred while retrieving session {session_id} for organization {org_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the session."
        )

    except Exception as e:
        # Handle any other unexpected errors
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the session."
        )
