from multiprocessing.connection import Client
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.middleware import Middleware

from app.helpers import get_jwt_claims
from app.middlewares.ClientAuthMiddleware import ClientAuthMiddleware
from app.middlewares.MiddlewareWrapper import middlewareWrapper
from app.payloads.request.ArenaAssociateRequest import ArenaAssociateRequest
from app.payloads.request.ArenaCreateRequest import ArenaCreateRequest
from app.payloads.request.ArenaDisassociationRequest import ArenaDisassociationRequest
from app.payloads.request.ArenaUpdateRequest import ArenaUpdateRequest
from app.payloads.request.GroupCreateRequest import GroupCreateRequest
from app.payloads.request.GroupUpdateRequest import GroupUpdateRequest
from app.payloads.request.SessionUpdateRequest import SessionUpdateRequest
from app.payloads.response.ArenaResponseTop import ArenaResponseTop
from app.payloads.response.GroupClientResponse import GroupClientResponse
from app.payloads.response.SessionResponse import SessionResponse, SessionCreateRequest
from app.services import arena as service
from app.database import get_db
from uuid import UUID
from sqlalchemy.exc import NoResultFound

router = APIRouter(
    route_class=middlewareWrapper(middlewares=[ClientAuthMiddleware])
)

# ---------------- Group Routes ----------------

@router.post("/groups", response_model=GroupClientResponse)
def create_group(group: GroupCreateRequest, db: Session = Depends(get_db),
                 jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")

    return service.create_group(db, group, org_id)


@router.get("/groups", response_model=list[GroupClientResponse])
def list_groups(db: Session = Depends(get_db), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    return service.get_groups(db, org_id)


@router.get("/groups/{group_id}", response_model=GroupClientResponse)
def get_group(group_id: str, db: Session = Depends(get_db), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    group = service.get_group(db, group_id, org_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.put("/groups/{group_id}", response_model=GroupClientResponse)
def update_group(group_id: str, group: GroupUpdateRequest, db: Session = Depends(get_db),
                 jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return service.update_group(db, group_id, group, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Group not found")


@router.delete("/groups/{group_id}")
def delete_group(group_id: str, db: Session = Depends(get_db), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return service.delete_group(db, group_id, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Group not found")


# ---------------- Arena Routes ----------------

@router.post("/arenas", response_model=ArenaResponseTop)
def create_arena(arena: ArenaCreateRequest, db: Session = Depends(get_db),
                 jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    return service.create_arena(db, arena, org_id)


@router.get("/arenas", response_model=list[ArenaResponseTop])
def list_arenas(db: Session = Depends(get_db), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    return service.get_arenas(db, org_id)


@router.get("/arenas/{arena_id}", response_model=ArenaResponseTop)
def get_arena(arena_id: UUID, db: Session = Depends(get_db), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    arena = service.get_arena(db, arena_id, org_id)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")
    return arena


@router.put("/arenas/{arena_id}", response_model=ArenaResponseTop)
def update_arena(arena_id: UUID, arena: ArenaUpdateRequest, db: Session = Depends(get_db),
                 jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return service.update_arena(db, arena_id, arena, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena not found")


@router.delete("/arenas/{arena_id}")
def delete_arena(arena_id: UUID, db: Session = Depends(get_db), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return service.delete_arena(db, arena_id, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena not found")


# Associate an arena with an additional group
@router.post("/arenas/{arena_id}/associate", response_model=dict)
def associate_arena(arena_id: UUID, association: ArenaAssociateRequest, db: Session = Depends(get_db),
                    jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return service.associate_arena_with_group(db, arena_id, association.group_id, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena or Group not found")


# Dissociate an arena from a specific group
@router.post("/arenas/{arena_id}/dissociate", response_model=dict)
def dissociate_arena(arena_id: UUID, dissociation: ArenaDisassociationRequest, db: Session = Depends(get_db),
                     jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return service.dissociate_arena_from_group(db, arena_id, dissociation.group_id, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena, Group, or Association not found")


# ---------------- Session Routes ----------------

@router.post("/sessions", response_model=SessionResponse)
def create_session(session: SessionCreateRequest, db: Session = Depends(get_db),
                   jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    return service.create_session(db, session, org_id)


@router.get("/sessions", response_model=list[SessionResponse])
def list_sessions(db: Session = Depends(get_db), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    return service.get_sessions(db, org_id)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    session = service.get_session(db, session_id, org_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.put("/sessions/{session_id}", response_model=SessionResponse)
def update_session(session_id: str, session: SessionUpdateRequest, db: Session = Depends(get_db),
                   jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return service.update_session(db, session_id, session, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Session not found")


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db),
                   jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    try:
        return service.delete_session(db, session_id, org_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Session not found")
