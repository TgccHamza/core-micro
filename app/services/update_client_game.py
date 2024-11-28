from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import Project
import logging

from app.payloads.request.GameUpdateRequest import GameUpdateRequest
from app.payloads.response.GameConfigResponse import GameConfigResponse

logger = logging.getLogger(__name__)

def update_client_game(
    db: Session,
    org_id: str,
    project_id: str,
    update_data: GameUpdateRequest
) -> GameConfigResponse:
    """
    Update a client game project with the provided data.
    :param db: Database session
    :param org_id: Organisation ID
    :param project_id: Project ID
    :param update_data: GameUpdateRequest containing fields to update
    :return: Updated project as ProjectResponse schema
    """
    # Fetch the project by organisation ID and project ID
    project = (
        db.query(Project)
        .filter(Project.organisation_code == org_id, Project.id == project_id)
        .first()
    )

    if not project:
        logger.warning(f"Project with ID {project_id} for organisation {org_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Update only provided fields dynamically
    update_fields = {
        key: value for key, value in update_data.dict(exclude_unset=True).items()
    }
    for field, value in update_fields.items():
        setattr(project, field, value)

    try:
        # Commit changes to the database
        db.commit()
        db.refresh(project)

        logger.info(f"Project with ID {project_id} updated successfully for organisation {org_id}.")
        return GameConfigResponse.from_orm(project)

    except Exception as e:
        logger.error(f"Error updating project with ID {project_id} for organisation {org_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the project"
        )
