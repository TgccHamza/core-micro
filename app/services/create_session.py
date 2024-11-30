from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from app.models import (Project, Arena, ArenaSession, SessionStatus, ActivationStatus, AccessStatus, ViewAccess)
from app.payloads.request.SessionCreateRequest import SessionCreateRequest
from app.repositories.get_arena_by_id import get_arena_by_id
from app.repositories.get_game_by_id import get_game_by_id


async def get_project(db: AsyncSession, org_id: str, project_id: str) -> Project:
    project = await get_game_by_id(project_id, org_id, db)
    if not project:
        raise NoResultFound(f"Project with ID {project_id} not found in organization {org_id}")
    return project


async def get_arena(db: AsyncSession, org_id: str, arena_id: str) -> Arena:
    arena = await get_arena_by_id(arena_id, db)
    if not arena:
        raise NoResultFound(f"Arena with ID {arena_id} not found in organization {org_id}")
    return arena


async def create_arena_session(
    db: AsyncSession, session_data: SessionCreateRequest, project: Project, org_id: str
) -> ArenaSession:
    arena_session = ArenaSession(
        arena_id=str(session_data.arena_id),
        project_id=str(session_data.game_id),
        session_status=SessionStatus.PENDING,
        activation_status=ActivationStatus.INACTIVE,
        access_status=AccessStatus.AUTH,
        view_access=ViewAccess.SESSION,
        organisation_code=org_id,
        player_module_id=str(project.module_game_id),
        gamemaster_module_id=str(project.module_gamemaster_id),
        super_game_master_module_id=str(project.module_super_game_master_id),
    )
    db.add(arena_session)
    await db.commit()
    await db.refresh(arena_session)
    return arena_session


async def create_session(db: AsyncSession, session_request: SessionCreateRequest, org_id: str) -> ArenaSession:
    project = await get_project(db, org_id, str(session_request.game_id))
    await get_arena(db, org_id, str(session_request.arena_id))
    return await create_arena_session(db, session_request, project, org_id)
