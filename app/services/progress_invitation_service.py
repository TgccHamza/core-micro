import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from fastapi import HTTPException

from app.enums import EmailStatus
from app.models import ArenaSession, ArenaSessionPlayers
from app.payloads.request.webhook_invitation_progress_request import WebhookInvitationProgressRequest, InvitationStatus, \
    RoleType

logger = logging.getLogger(__name__)


async def progress_invitation_service(db: AsyncSession, data: WebhookInvitationProgressRequest):
    """
    Processes invitation progress updates by updating the database based on the webhook data.

    Args:
        db (AsyncSession): SQLAlchemy asynchronous database session.
        data (WebhookInvitationProgressRequest): Webhook payload containing progress information.

    Returns:
        dict: A dictionary with a success message.
    """
    try:
        # Step 1: Validate session existence
        result = await db.execute(select(ArenaSession).filter_by(id=data.session_id))
        session = result.scalars().first()
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session with ID {data.session_id} not found."
            )

        if data.role.value == RoleType.PLAYER.value:
            for user_data in data.users:
                result = await db.execute(
                    select(ArenaSessionPlayers).filter_by(
                        session_id=data.session_id,
                        user_id=user_data.id
                    )
                )
                player = result.scalars().first()

                if player:
                    # Update player email status to reflect the progress
                    player.email_status = EmailStatus.DELIVERED if data.status == InvitationStatus.INVITATION_ACCEPTED else EmailStatus.SENT
                else:
                    # Optionally create a new player if not found
                    new_player = ArenaSessionPlayers(
                        session_id=data.session_id,
                        user_id=user_data.id,
                        is_game_master=False,
                        email_status=EmailStatus.SENT
                    )
                    db.add(new_player)
        elif data.role.value == RoleType.GAME_MASTER.value:
            for user_data in data.users:
                result = await db.execute(
                    select(ArenaSessionPlayers).filter_by(
                        session_id=data.session_id,
                        user_id=user_data.id
                    )
                )
                player = result.scalars().first()

                if player:
                    # Update player email status to reflect the progress
                    player.email_status = EmailStatus.DELIVERED if data.status == InvitationStatus.INVITATION_ACCEPTED else EmailStatus.SENT
                else:
                    # Optionally create a new player if not found
                    new_player = ArenaSessionPlayers(
                        session_id=data.session_id,
                        user_id=user_data.id,
                        is_game_master=True,
                        email_status=EmailStatus.SENT
                    )
                    db.add(new_player)
        elif data.role.value == RoleType.MODERATOR.value:
            logger.error("Moderator condition has been enter")
            for user_data in data.users:
                logger.error("users has been looped")
                # Update player email status to reflect the progress
                session.email_status = EmailStatus.DELIVERED if data.status == InvitationStatus.INVITATION_ACCEPTED else EmailStatus.SENT
                session.super_game_master_id = user_data.id
                db.add(session)

        # Commit all changes to the database
        await db.commit()

        return {"message": "Invitation progress updated successfully."}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error occurred: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error occurred: {str(e)}"
        )
