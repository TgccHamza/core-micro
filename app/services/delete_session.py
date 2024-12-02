import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.exceptions.NoResultFoundError import NoResultFoundError
from app.models import ArenaSessionPlayers
from app.repositories.get_players_by_session import get_players_by_session
from app.services.get_session import get_session

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def delete_session(db: AsyncSession, session_id: str, org_id: str):
    """
    Deletes a session and its associated players from the database.

    Args:
        db (Session): Database session.
        session_id (str): ID of the session to be deleted.
        org_id (str): Organization ID that the session belongs to.

    Returns:
        dict: Confirmation message indicating the session was deleted.

    Raises:
        HTTPException: If the session is not found or if there is a database error.
    """
    try:
        # Fetch the session to be deleted
        db_session = get_session(db, session_id, org_id)
        if not db_session:
            logger.warning(f"Session {session_id} not found for organization {org_id}.")
            raise NoResultFoundError(f"Session with ID {session_id} not found in the organization.")

        # Delete players associated with the session
        players = await get_players_by_session(session_id, db)
        await db.delete(players)
        logger.info(f"Deleted players for session {session_id}.")

        # Delete the session itself
        await db.delete(db_session)
        logger.info(f"Deleted session {session_id}.")

        # Commit changes to the database
        await db.commit()
        logger.info(f"Session {session_id} deleted successfully.")

        return {"message": "Session deleted successfully"}

    except SQLAlchemyError as e:
        # Handle database-related errors (e.g., connection issues, integrity errors)
        await db.rollback()  # Ensure the transaction is rolled back in case of error
        logger.error(f"Database error occurred while deleting session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the session."
        )

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )
