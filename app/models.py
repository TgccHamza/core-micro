import uuid
from sqlalchemy import Column, String, Enum, Integer, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from .enums import AccessStatus, PeriodType, SessionStatus, ViewAccess, ActivationStatus

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), index=True)
    description = Column(String(255), index=True)
    db_index = Column(String(36), index=True)
    slug = Column(String(255), unique=True, index=True)
    visibility = Column(String(50), default="public")  # Default visibility is public
    activation_status = Column(Enum(ActivationStatus), default=ActivationStatus.ACTIVE)
    client_id = Column(String(36), nullable=True, index=True, default=lambda: str(uuid.uuid4()))
    client_name = Column(String(255), nullable=True, index=True)  # Client name for easy access

    # Updated relationship with primaryjoin
#     modules = relationship(
#         "ProjectModule",
#         primaryjoin="Project.id == ProjectModule.project_id",
#         back_populates="project"
#     )

class ProjectModule(Base):
    __tablename__ = "project_modules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), index=True)
    type = Column(String(50))  # E.g., game, leaderboard, monitor
    project_id = Column(String(36), index=True)  # No ForeignKey constraint

    # New fields
    order = Column(Integer, nullable=False, default=0)  # Module order within the project

    # Updated relationship with primaryjoin
#     project = relationship(
#         "Project",
#         primaryjoin="ProjectModule.project_id == Project.id",
#         back_populates="modules"
#     )

# Group model
class Group(Base):
    __tablename__ = "groups"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)

    # Relationships
#     users = relationship("GroupUsers", back_populates="group")
#     projects = relationship("GroupProjects", back_populates="group")
#     arenas = relationship("GroupArenas", back_populates="group")

# GroupUsers model
class GroupUsers(Base):
    __tablename__ = "group_users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String(36))  # No ForeignKey constraint
    user_id = Column(String(36))   # No ForeignKey constraint

    # Relationships
#     group = relationship("Group", back_populates="users")
#     user = relationship("User")

# GroupProjects model
class GroupProjects(Base):
    __tablename__ = "group_projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String(36))  # No ForeignKey constraint
    project_id = Column(String(36))  # No ForeignKey constraint

    # Relationships
#     group = relationship("Group", back_populates="projects")
#     project = relationship("Project", primaryjoin="GroupProjects.project_id == Project.id")

# GroupArenas model
class GroupArenas(Base):
    __tablename__ = "group_arenas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String(36))  # No ForeignKey constraint
    arena_id = Column(String(36))  # No ForeignKey constraint

    # Relationships
#     group = relationship("Group", back_populates="arenas")
#     arena = relationship("Arena", primaryjoin="GroupArenas.arena_id == Arena.id")

# Arena model
class Arena(Base):
    __tablename__ = "arenas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)

    # Relationships
#     sessions = relationship("ArenaSession", back_populates="arena")

# ArenaSession model
class ArenaSession(Base):
    __tablename__ = "arena_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    arena_id = Column(String(36))  #No ForeignKey constraint
    project_id = Column(String(36))  #No ForeignKey constraint
    module_id = Column(String(36))  #No ForeignKey constraint
    period_type = Column(Enum(PeriodType), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    access_status = Column(Enum(AccessStatus), nullable=False)
    session_status = Column(Enum(SessionStatus), nullable=False)
    view_access = Column(Enum(ViewAccess), nullable=False)

    # Relationships
#     arena = relationship("Arena", back_populates="sessions")
#     players = relationship("ArenaSessionPlayers", back_populates="session")

# ArenaSessionPlayers model
class ArenaSessionPlayers(Base):
    __tablename__ = "arena_session_players"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36))  # No ForeignKey constraint
    user_id = Column(String(36))      # No ForeignKey constraint

    # Relationships
#     session = relationship("ArenaSession", back_populates="players")
#     user = relationship("User")
