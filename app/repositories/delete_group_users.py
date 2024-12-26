from sqlalchemy.ext.asyncio import AsyncSession


async def delete_group_users(db: AsyncSession, group_id: str):
    await db.execute(
        "DELETE FROM group_users WHERE group_id = :group_id",
        {"group_id": group_id},
    )