from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID

from starlette import status

from app.models import Arena
from app.payloads.request import ArenaUpdateRequest
from app.repositories.get_arena_by_id import get_arena_by_id


async def update_arena(db: AsyncSession, arena_id: UUID, arena_request: ArenaUpdateRequest, org_id: str) -> Arena:
    """
    Update an Arena's details.

    Args:
        db (Session): The database session.
        arena_id (UUID): The ID of the Arena to update.
        arena_request (ArenaUpdateRequest): The updated details for the Arena.
        org_id (str): The organization code for validation.

    Returns:
        Arena: The updated Arena object.

    Raises:
        ValueError: If the Arena is not found or if the update request is invalid.
        RuntimeError: If any database error occurs during the operation.
    """
    try:

        # Retrieve the Arena
        arena = await get_arena_by_id(str(arena_id), db)
        if arena.organisation_code != org_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"message": "Arena not allowed for this organisation"})

        # Update fields conditionally
        if arena_request.name is not None:
            arena.name = arena_request.name

        # Commit the changes
        await db.commit()
        await db.refresh(arena)
        return arena
    except ValueError as e:
        await db.rollback()
        raise e
    except SQLAlchemyError as e:
        await db.rollback()
        raise RuntimeError(f"Database error occurred while updating Arena {arena_id}: {e}")
