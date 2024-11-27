from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from app.models import (Project, Arena, ArenaSession, SessionStatus, ActivationStatus, AccessStatus, ViewAccess)
from app.payloads.request.SessionCreateRequest import SessionCreateRequest


def get_project(db: Session, org_id: str, project_id: str) -> Project:
    project = (
        db.query(Project)
        .filter(Project.organisation_code == org_id, Project.id == project_id)
        .first()
    )
    if not project:
        raise NoResultFound(f"Project with ID {project_id} not found in organization {org_id}")
    return project


def get_arena(db: Session, org_id: str, arena_id: str) -> Arena:
    arena = (
        db.query(Arena)
        .filter(Arena.organisation_code == org_id, Arena.id == arena_id)
        .first()
    )
    if not arena:
        raise NoResultFound(f"Arena with ID {arena_id} not found in organization {org_id}")
    return arena


def create_arena_session(
    db: Session, session_data: SessionCreateRequest, project: Project, org_id: str
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
    db.commit()
    db.refresh(arena_session)
    return arena_session


def create_session(db: Session, session_request: SessionCreateRequest, org_id: str) -> ArenaSession:
    project = get_project(db, org_id, str(session_request.game_id))
    get_arena(db, org_id, str(session_request.arena_id))
    return create_arena_session(db, session_request, project, org_id)
