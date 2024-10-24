import uuid
from sqlalchemy import Column, String, ForeignKey, BINARY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID  # Use this if you're on PostgreSQL
from .database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), index=True)
    slug = Column(String(255), unique=True, index=True)
    domain = Column(String(255),nullable=True, default=lambda: f"{generate_random_subdomain()}.thegamechangercompany.io", index=True)
    visibility = Column(String(50), default="public")  # Default visibility is public
    client_id = Column(String(36),nullable=True, index=True, default=lambda:  str(uuid.uuid4()))
    client_name = Column(String(255),nullable=True, index=True)  # Client name for easy access

    modules = relationship("ProjectModule", back_populates="project")  # Updated relationship

class ProjectModule(Base):  # Changed from ProjectPart to ProjectModule
    __tablename__ = "project_modules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), index=True)
    type = Column(String(50))  # E.g., game, leaderboard, monitor
    db_index = Column(String(255))  # Assuming this is a string for MongoDB index reference
    project_id = Column(String(36), ForeignKey('projects.id'), index=True, default=lambda: uuid.uuid4().bytes)

    project = relationship("Project", back_populates="modules")  # Updated relationship
