from pydantic import BaseModel, Field, constr
from typing import List, Optional
from uuid import UUID

class ProjectBase(BaseModel):
    name: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=255)
    domain: Optional[str] = Field(..., max_length=255)
    visibility: Optional[str] = Field(default='public', pattern=r'^(public|private|unlisted)$')
    client_id: Optional[UUID]   # UUID for client_id
    client_name: Optional[str] = Field(..., max_length=255)  # Name of the client

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class Project(ProjectBase):
    id: UUID  # Use UUID instead of int
    modules: List["ProjectModule"] = []  # Updated to use ProjectModule

    class Config:
        orm_mode = True

class ProjectModuleBase(BaseModel):  # Updated from ProjectPartBase to ProjectModuleBase
    name: str = Field(..., max_length=255)
    type: str = Field(..., max_length=50)  # E.g., game, leaderboard, monitor
    db_index: Optional[str] = None

class ProjectModuleCreate(ProjectModuleBase):  # Updated from ProjectPartCreate
    project_id: UUID  # Ensure the project_id is UUID

class ProjectModuleUpdate(ProjectModuleBase):  # Updated from ProjectPartUpdate
    pass

class ProjectModule(ProjectModuleBase):  # Updated from ProjectPart
    id: UUID  # Use UUID instead of int
    project: Project  # Reference to the parent Project

    class Config:
        orm_mode = True

# Update forward reference for List of ProjectM
