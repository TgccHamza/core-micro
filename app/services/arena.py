from sqlalchemy.orm import Session
from .. import models
from ..schemas import GroupCreate, GroupUpdate, ArenaCreate, ArenaUpdate, SessionCreate, SessionUpdate
from sqlalchemy.exc import NoResultFound
from uuid import UUID
from sqlalchemy.exc import NoResultFound

# ---------------- Group CRUD Operations ----------------

def create_group(db: Session, group: GroupCreate):
    db_group = models.Group(name=group.name)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    for user_id in group.user_ids:
        db_user_group = models.GroupUsers(group_id=db_group.id, user_id=user_id)
        db.add(db_user_group)

    for project_id in group.project_ids:
        db_project_group = models.GroupProjects(group_id=db_group.id, project_id=project_id)
        db.add(db_project_group)

    db.commit()
    return db_group

def get_groups(db: Session):
    return db.query(models.Group).all()

def get_group(db: Session, group_id: str):
    return db.query(models.Group).filter(models.Group.id == group_id).first()

def update_group(db: Session, group_id: str, group: GroupUpdate):
    db_group = get_group(db, group_id)
    if not db_group:
        raise NoResultFound("Group not found")

    db_group.name = group.name

    # Update Users
    db.query(models.GroupUsers).filter(models.GroupUsers.group_id == group_id).delete()
    for user_id in group.user_ids:
        db_user_group = models.GroupUsers(group_id=group_id, user_id=user_id)
        db.add(db_user_group)

    # Update Projects
    db.query(models.GroupProjects).filter(models.GroupProjects.group_id == group_id).delete()
    for project_id in group.project_ids:
        db_project_group = models.GroupProjects(group_id=group_id, project_id=project_id)
        db.add(db_project_group)

    db.commit()
    return db_group

def delete_group(db: Session, group_id: str):
    db_group = get_group(db, group_id)
    if not db_group:
        raise NoResultFound("Group not found")

    db.query(models.GroupUsers).filter(models.GroupUsers.group_id == group_id).delete()
    db.query(models.GroupProjects).filter(models.GroupProjects.group_id == group_id).delete()
    db.delete(db_group)
    db.commit()
    return {"message": "Group deleted successfully"}

# ---------------- Arena CRUD Operations ----------------

# Create an Arena and associate it with a single group
def create_arena(db: Session, arena: ArenaCreate):
    db_arena = models.Arena(name=arena.name)
    db.add(db_arena)
    db.commit()
    db.refresh(db_arena)

    # Associate the arena with the specified group
    group_association = models.GroupArenas(group_id=str(arena.group_id), arena_id=db_arena.id)
    db.add(group_association)
    db.commit()
    return db_arena

# Get all Arenas with their associated groups
def get_arenas(db: Session):
    return db.query(models.Arena).all()

# Get a specific Arena by ID
def get_arena(db: Session, arena_id: UUID):
    return db.query(models.Arena).filter(models.Arena.id == str(arena_id)).first()

# Update Arena name only (group association updates are not allowed here)
def update_arena(db: Session, arena_id: UUID, arena: ArenaUpdate):
    db_arena = get_arena(db, arena_id)
    if not db_arena:
        raise NoResultFound("Arena not found")

    if arena.name is not None:
        db_arena.name = arena.name

    db.commit()
    return db_arena

# Delete an Arena
def delete_arena(db: Session, arena_id: UUID):
    db_arena = get_arena(db, arena_id)
    if not db_arena:
        raise NoResultFound("Arena not found")

    db.query(models.GroupArenas).filter(models.GroupArenas.arena_id == str(arena_id)).delete()
    db.delete(db_arena)
    db.commit()
    return {"message": "Arena deleted successfully"}

# Associate an Arena with an additional group
def associate_arena_with_group(db: Session, arena_id: UUID, group_id: UUID):
    association = models.GroupArenas(group_id=str(group_id), arena_id=str(arena_id))
    db.add(association)
    db.commit()
    return {"message": f"Arena {arena_id} associated with Group {group_id}"}

# Dissociate an Arena from a specific group
def dissociate_arena_from_group(db: Session, arena_id: UUID, group_id: UUID):
    association = db.query(models.GroupArenas).filter(
        models.GroupArenas.arena_id == str(arena_id),
        models.GroupArenas.group_id == str(group_id)
    ).first()

    if association:
        db.delete(association)
        db.commit()
        return {"message": f"Arena {arena_id} dissociated from Group {group_id}"}
    else:
        raise NoResultFound("Association not found")


# ---------------- Session CRUD Operations ----------------

def create_session(db: Session, session: SessionCreate):
    db_session = models.ArenaSession(
        arena_id=str(session.arena_id),
        project_id=str(session.project_id),
        module_id=str(session.module_id),
        period_type=session.period_type,
        start_time=session.start_time,
        end_time=session.end_time,
        access_status=session.access_status,
        session_status=session.session_status,
        view_access=session.view_access
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    for user_id in session.user_ids:
        db_player = models.ArenaSessionPlayers(session_id=db_session.id, user_id=str(user_id))
        db.add(db_player)

    db.commit()
    return db_session

def get_sessions(db: Session):
    return db.query(models.ArenaSession).all()

def get_session(db: Session, session_id: str):
    return db.query(models.ArenaSession).filter(models.ArenaSession.id == session_id).first()

def update_session(db: Session, session_id: str, session: SessionUpdate):
    db_session = get_session(db, session_id)
    if not db_session:
        raise NoResultFound("Session not found")

    db_session.period_type = session.period_type
    db_session.start_time = session.start_time
    db_session.end_time = session.end_time
    db_session.access_status = session.access_status
    db_session.session_status = session.session_status
    db_session.view_access = session.view_access
    db_session.project_id = session.project_id
    db_session.module_id = session.module_id

    # Update Players
    db.query(models.ArenaSessionPlayers).filter(models.ArenaSessionPlayers.session_id == session_id).delete()
    for user_id in session.user_ids:
        db_player = models.ArenaSessionPlayers(session_id=session_id, user_id=user_id)
        db.add(db_player)

    db.commit()
    return db_session

def delete_session(db: Session, session_id: str):
    db_session = get_session(db, session_id)
    if not db_session:
        raise NoResultFound("Session not found")

    db.query(models.ArenaSessionPlayers).filter(models.ArenaSessionPlayers.session_id == session_id).delete()
    db.delete(db_session)
    db.commit()
    return {"message": "Session deleted successfully"}
