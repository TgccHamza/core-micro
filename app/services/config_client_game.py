from fastapi import HTTPException, status

from app.models import Project


def get_project(db, org_id: str, project_id: str):
    """
    Retrieves a project by its organisation code and project ID.

    Args:
        db: The database session instance.
        org_id (str): The organisation code.
        project_id (int): The project ID.

    Returns:
        Project: The project instance if found.

    Raises:
        HTTPException: If the project is not found.
    """
    project = db.query(Project).filter(
        Project.organisation_code == org_id,
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} for organisation {org_id} not found."
        )

    return project


def config_client_game(db, org_id: str, project_id: str):
    """
    Configures the client game by fetching the associated project.

    Args:
        db: The database session instance.
        org_id (str): The organisation code.
        project_id (int): The project ID.

    Returns:
        Project: The project instance.
    """
    project = get_project(db, org_id, project_id)

    # Additional logic for configuring the game can go here, such as client-specific settings.

    return project
