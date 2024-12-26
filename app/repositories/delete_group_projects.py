from sqlalchemy.ext.asyncio import AsyncSession


async def delete_group_projects(db: AsyncSession, group_id: str):
    await db.execute(
        "DELETE FROM group_projects WHERE group_id = :group_id",
        {"group_id": group_id},
    )