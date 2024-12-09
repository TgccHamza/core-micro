from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.PlayerNotFoundError import PlayerNotFoundError
from app.repositories.get_player_by_id import get_player_by_id


async def remove_player_from_session(db: AsyncSession, session_player_id: str, org_id: str):
    """
    Validates that the player exists in the session and removes them.
    Handles the logic of verifying the player's existence and association with the organization.
    """
    # Validate if the player exists and belongs to the correct organization
    session_player = await get_player_by_id(session_player_id, org_id, db)

    if not session_player:
        # Raise a custom exception for better error handling
        raise PlayerNotFoundError(f"Session Player with ID {session_player_id} not found.")

    # Remove the player from the session
    await db.delete(session_player)
    await db.commit()
