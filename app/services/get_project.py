from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import Project


def get_project(db: Session, project_id: str) -> Project:
    """
    Fetches a project by its ID from the database.

    Args:
        db (Session): The database session instance.
        project_id (str): The ID of the project.

    Returns:
        Project: The project instance if found.

    Raises:
        HTTPException: If the project is not found.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found."
        )

    return project
