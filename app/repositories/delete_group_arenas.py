from sqlalchemy.ext.asyncio import AsyncSession


async def delete_group_arenas(db: AsyncSession, group_id: str):
    await db.execute(
        "DELETE FROM group_arenas WHERE group_id = :group_id",
        {"group_id": group_id},
    )
