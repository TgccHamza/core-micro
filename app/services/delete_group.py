from sqlalchemy.ext.asyncio import AsyncSession
from app.payloads.response.DeleteGroupResponse import DeleteGroupResponse
from app.repositories.delete_group_arenas import delete_group_arenas
from app.repositories.delete_group_projects import delete_group_projects
from app.repositories.delete_group_users import delete_group_users
from app.services.get_group import get_group


async def delete_group(db: AsyncSession, group_id: str, org_id: str) -> DeleteGroupResponse:
    """
    Deletes a group from the system and removes its associations with arenas.

    Args:
        db (AsyncSession): The database session.
        group_id (str): The ID of the group to delete.
        org_id (str): The organization ID associated with the group.

    Returns:
        DeleteGroupResponse: True if the group was successfully deleted, False otherwise.
    """

    try:
        # Validate existence of the group
        group = await get_group(db, group_id, org_id)
        # Remove associations from GroupArenas table
        await remove_associations_from_group(db, group_id)

        # Delete the group
        await db.delete(group)
        await db.commit()
        return DeleteGroupResponse(
            message="Group deleted successfully.",
            group_id=group_id,
        )
    except Exception as ex:
        await db.rollback()  # Rollback transaction in case of an error
        raise ex


async def remove_associations_from_group(db: AsyncSession, group_id: str):
    """
    Removes all arena associations related to the group before deletion.

    Args:
        db (Session): The database session.
        group_id (str): The ID of the group to remove associations from.
    """
    # Find and delete all associations of this group in the GroupArenas table
    """
    delete_group_users: Function to delete from `GroupUsers` table.
    delete_group_projects: Function to delete from `GroupProjects` table.
    delete_group_arenas: Function to delete from `GroupArenas` table.
    """
    await delete_group_users(db, group_id)
    await delete_group_projects(db, group_id)
    await delete_group_arenas(db, group_id)
    await db.commit()
