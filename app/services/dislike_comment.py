from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import ProjectComment, CommentLike


def dislike_comment(db: Session, comment_id: str, user_id: str) -> ProjectComment:
    """
    Remove a user's like from a comment.

    Args:
        db (Session): The database session.
        comment_id (str): The ID of the comment.
        user_id (str): The ID of the user.

    Returns:
        ProjectComment: The updated comment instance.

    Raises:
        HTTPException: If the like does not exist or if an error occurs during processing.
    """
    # Retrieve the existing like for the comment by the user
    comment_like = db.query(CommentLike).filter(
        CommentLike.comment_id == comment_id,
        CommentLike.user_id == user_id
    ).first()

    # Raise an exception if the like does not exist
    if not comment_like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found for the specified comment and user",
        )

    # Retrieve the associated comment
    comment = comment_like.comment

    try:
        # Remove the like from the database
        db.delete(comment_like)
        db.commit()
    except Exception as e:
        db.rollback()  # Ensure the transaction is rolled back on error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while disliking the comment",
        ) from e

    return comment
