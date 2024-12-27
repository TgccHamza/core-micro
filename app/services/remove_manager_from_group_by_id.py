from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select
from app.exceptions.not_found_exception import NotFoundException
from app.models import GroupUsers

from app.payloads.response.RemoveManagerFromGroupByIdResponse import RemoveManagerFromGroupByIdResponse

async def remove_manager_from_group_by_id(
        group_manager_id: str, 
        db: AsyncSession
) -> RemoveManagerFromGroupByIdResponse:
    """
    Remove a manager from a group by their ID.
    This function removes a manager from a group in the database by their ID. 
    It first checks if the manager exists in the group, and if not, raises a NotFoundException. 
    If the manager exists, it removes the manager from the group and commits the changes to the database.
    Args:
        group_manager_id (str): The ID of the manager to be removed from the group.
        db (AsyncSession): The asynchronous database session.
    Returns:
        RemoveManagerFromGroupByIdResponse: A response object indicating the success of the operation.
    Raises:
        NotFoundException: If the manager with the given ID is not found in the group.
    """

    # Check if manager exists
    manager_query = await db.execute(
        select(GroupUsers).filter_by(id=group_manager_id)
    )
    manager = manager_query.scalars().first()

    if not manager:
        raise NotFoundException(
            error="Manager with this id is not assigned to the group"
        )

    # Remove manager
    await db.delete(manager)
    await db.flush()
    await db.commit()
    return RemoveManagerFromGroupByIdResponse(
        message="Manager removed from group successfully"
    )
