from sqlalchemy.orm import Session
from app.models import ArenaSessionPlayers
from app.exceptions.PlayerNotFoundError import PlayerNotFoundError


def remove_player_from_session(db: Session, session_player_id: str, org_id: str):
    """
    Validates that the player exists in the session and removes them.
    Handles the logic of verifying the player's existence and association with the organization.
    """
    # Validate if the player exists and belongs to the correct organization
    session_player = db.query(ArenaSessionPlayers).filter(
        ArenaSessionPlayers.id == session_player_id,
        ArenaSessionPlayers.organisation_code == org_id
    ).first()

    if not session_player:
        # Raise a custom exception for better error handling
        raise PlayerNotFoundError(f"Session Player with ID {session_player_id} not found.")

    # Remove the player from the session
    db.delete(session_player)
    db.commit()
