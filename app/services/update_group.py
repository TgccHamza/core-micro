from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
import logging

from app.models import GroupProjects
from app.payloads.request.GroupUpdateRequest import GroupUpdateRequest
from app.services.get_group import get_group

# Set up logging
logger = logging.getLogger(__name__)


def update_group(db: Session, group_id: str, group: GroupUpdateRequest, org_id: str):
    try:
        # Fetch the existing group from the database
        db_group = get_group(db, group_id, org_id)
        if not db_group:
            raise NoResultFound(f"Group with ID {group_id} not found in organization {org_id}")

        # Update group details
        db_group.name = group.name

        # Delete old project associations
        db.query(GroupProjects).filter(GroupProjects.group_id == group_id).delete(
            synchronize_session=False)

        # Add new project associations
        for project_id in group.project_ids:
            db_project_group = GroupProjects(group_id=group_id, project_id=project_id)
            db.add(db_project_group)

        # Commit the changes to the database
        db.commit()

        # Log the successful update
        logger.info(f"Group with ID {group_id} updated successfully in organization {org_id}")

        return db_group

    except NoResultFound as e:
        # Log and re-raise the not found error
        logger.error(f"Group not found: {str(e)}")
        db.rollback()
        raise e

    except SQLAlchemyError as e:
        # Log any database-related errors
        logger.error(f"Database error occurred while updating group {group_id}: {str(e)}")
        db.rollback()
        raise Exception("A database error occurred while updating the group.")

    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error occurred: {str(e)}")
        db.rollback()
        raise Exception(f"An unexpected error occurred: {str(e)}")
