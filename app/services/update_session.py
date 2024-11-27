import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import ArenaSession
from app.payloads.request import SessionUpdateRequest
from app.services.get_session import get_session

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def validate_session_update(session: SessionUpdateRequest):
    """
    Validates the session update request.

    Args:
        session (SessionUpdateRequest): The session configuration request to validate.

    Returns:
        bool: True if the session configuration is valid, raises exceptions otherwise.
    """
    if not session.start_time or not session.end_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start time and end time are required.")

    if session.start_time >= session.end_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start time must be before end time.")

    # Add any additional business logic validation here as needed
    return True


def update_session(db: Session, session_id: str, session: SessionUpdateRequest, org_id: str):
    """
    Updates the session with the given details.

    Args:
        db (Session): The database session.
        session_id (str): The ID of the session to update.
        session (SessionUpdateRequest): The new session details.
        org_id (str): The organization ID associated with the session.

    Returns:
        ArenaSession: The updated session object.

    Raises:
        HTTPException: If the session is not found or there are validation errors.
    """
    try:
        # Validate the session update request
        validate_session_update(session)

        # Retrieve the session to be updated
        db_session = get_session(db, session_id, org_id)
        if not db_session:
            logger.warning(f"Session {session_id} not found for organization {org_id}.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        # Update session details
        db_session.period_type = session.period_type
        db_session.start_time = session.start_time
        db_session.end_time = session.end_time
        db_session.access_status = session.access_status
        db_session.session_status = session.session_status
        db_session.view_access = session.view_access
        db_session.project_id = session.project_id

        # Commit the changes to the database
        db.commit()

        logger.info(f"Session {session_id} successfully updated for organization {org_id}.")
        return db_session

    except SQLAlchemyError as e:
        # Log database errors and rollback transaction
        logger.error(f"Database error while updating session {session_id}: {str(e)}")
        db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating session.")

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error while updating session {session_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error occurred.")
