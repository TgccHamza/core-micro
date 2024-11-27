import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import ArenaSession
from app.payloads.request import SessionConfigRequest
from app.services.get_session import get_session

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def validate_session_config(session: SessionConfigRequest):
    """
    Validates the session configuration request.

    Args:
        session (SessionConfigRequest): The session configuration request to validate.

    Returns:
        bool: True if the session configuration is valid, raises exceptions otherwise.
    """
    if not session.start_time or not session.end_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start time and end time are required.")

    if session.start_time >= session.end_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start time must be before end time.")

    # Add more validation logic here if needed
    return True


def config_session(db: Session, session_id: str, session: SessionConfigRequest, org_id: str):
    """
    Configures the session with the given settings.

    Args:
        db (Session): The database session for querying.
        session_id (str): The ID of the session to configure.
        session (SessionConfigRequest): The new session configuration settings.
        org_id (str): The organization ID associated with the session.

    Returns:
        ArenaSession: The updated session object.

    Raises:
        HTTPException: If the session is not found, or if there are validation errors.
    """
    try:
        # Validate input session configuration
        validate_session_config(session)

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

        # Commit the changes to the database
        db.commit()

        logger.info(f"Session {session_id} successfully configured for organization {org_id}.")
        return db_session

    except SQLAlchemyError as e:
        logger.error(f"Database error while configuring session {session_id}: {str(e)}")
        db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error updating session configuration.")

    except Exception as e:
        logger.error(f"Unexpected error while configuring session {session_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error occurred.")
