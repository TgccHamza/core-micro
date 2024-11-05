from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas
from ..services import arena as service
from ..database import get_db
from uuid import UUID
from sqlalchemy.exc import NoResultFound

router = APIRouter()

# ---------------- Group Routes ----------------

@router.post("/groups/", response_model=schemas.Group)
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    return service.create_group(db, group)

@router.get("/groups/", response_model=list[schemas.Group])
def list_groups(db: Session = Depends(get_db)):
    return service.get_groups(db)

@router.get("/groups/{group_id}", response_model=schemas.Group)
def get_group(group_id: str, db: Session = Depends(get_db)):
    group = service.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.put("/groups/{group_id}", response_model=schemas.Group)
def update_group(group_id: str, group: schemas.GroupUpdate, db: Session = Depends(get_db)):
    try:
        return service.update_group(db, group_id, group)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Group not found")

@router.delete("/groups/{group_id}")
def delete_group(group_id: str, db: Session = Depends(get_db)):
    try:
        return service.delete_group(db, group_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Group not found")

# ---------------- Arena Routes ----------------

@router.post("/arenas/", response_model=schemas.Arena)
def create_arena(arena: schemas.ArenaCreate, db: Session = Depends(get_db)):
    return service.create_arena(db, arena)

@router.get("/arenas/", response_model=list[schemas.Arena])
def list_arenas(db: Session = Depends(get_db)):
    return service.get_arenas(db)

@router.get("/arenas/{arena_id}", response_model=schemas.Arena)
def get_arena(arena_id: UUID, db: Session = Depends(get_db)):
    arena = service.get_arena(db, arena_id)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")
    return arena

@router.put("/arenas/{arena_id}", response_model=schemas.Arena)
def update_arena(arena_id: UUID, arena: schemas.ArenaUpdate, db: Session = Depends(get_db)):
    try:
        return service.update_arena(db, arena_id, arena)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena not found")

@router.delete("/arenas/{arena_id}")
def delete_arena(arena_id: UUID, db: Session = Depends(get_db)):
    try:
        return service.delete_arena(db, arena_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena not found")

# Associate an arena with an additional group
@router.post("/arenas/{arena_id}/associate", response_model=dict)
def associate_arena(arena_id: UUID, association: schemas.ArenaAssociate, db: Session = Depends(get_db)):
    try:
        return service.associate_arena_with_group(db, arena_id, association.group_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena or Group not found")

# Dissociate an arena from a specific group
@router.post("/arenas/{arena_id}/dissociate", response_model=dict)
def dissociate_arena(arena_id: UUID, dissociation: schemas.ArenaDisassociation, db: Session = Depends(get_db)):
    try:
        return service.dissociate_arena_from_group(db, arena_id, dissociation.group_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Arena, Group, or Association not found")


# ---------------- Session Routes ----------------

@router.post("/sessions/", response_model=schemas.Session)
def create_session(session: schemas.SessionCreate, db: Session = Depends(get_db)):
    return service.create_session(db, session)

@router.get("/sessions/", response_model=list[schemas.Session])
def list_sessions(db: Session = Depends(get_db)):
    return service.get_sessions(db)

@router.get("/sessions/{session_id}", response_model=schemas.Session)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.put("/sessions/{session_id}", response_model=schemas.Session)
def update_session(session_id: str, session: schemas.SessionUpdate, db: Session = Depends(get_db)):
    try:
        return service.update_session(db, session_id, session)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Session not found")

@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    try:
        return service.delete_session(db, session_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Session not found")
