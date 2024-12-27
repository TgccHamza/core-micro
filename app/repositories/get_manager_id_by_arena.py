from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Arena, GroupUsers, GroupArenas

async def get_manager_ids_by_arena(db: AsyncSession, arena_id: str):
    # Query to get the manager IDs for all groups associated with the arena
    result = await db.execute(
        select(GroupUsers.user_id)
        .join(GroupArenas, GroupArenas.group_id == GroupUsers.group_id)
        .filter(GroupArenas.arena_id == arena_id)
    )
    
    manager_ids = result.scalars().all()
    
    return manager_ids