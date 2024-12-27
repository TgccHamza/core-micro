from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Arena

async def get_arena_by_id_and_org_id(arena_id: str, org_id: str, session: AsyncSession):
    stmt = select(Arena).where(Arena.id == arena_id, Arena.org_id == org_id)
    result = await session.execute(stmt)
    arena = result.scalars().first()
    return arena