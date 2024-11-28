from sqlalchemy.orm import Session
from app import models
from app.payloads.request.GroupCreateRequest import GroupCreateRequest
from app.services.invite_managers import invite_managers


# ---------------- Group CRUD Operations ----------------

def create_group(db: Session, group_request: GroupCreateRequest, org_id: str, background_tasks):
    """
    Creates a new group and associates it with projects and managers.
    """
    try:
        db_group = _create_group(db, group_request.name, org_id)
        _associate_projects_with_group(db, db_group.id, group_request.project_ids)
        invite_managers(db, db_group, group_request.managers, background_tasks)
        return db_group
    except Exception as e:
        db.rollback()  # Ensure to rollback in case of any error during the transaction
        raise RuntimeError(f"Error creating group: {str(e)}") from e


def _create_group(db: Session, group_name: str, org_id: str) -> models.Group:
    """
    Creates a group in the database.
    """
    db_group = models.Group(name=group_name, organisation_code=org_id)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def _associate_projects_with_group(db: Session, group_id: str, project_ids: list):
    """
    Associates a list of project IDs with a group.
    """
    project_group_mappings = [
        models.GroupProjects(group_id=group_id, project_id=project_id)
        for project_id in project_ids
    ]
    db.add_all(project_group_mappings)
    db.commit()
