from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import ProjectComment, CommentLike


def like_comment(db: Session, comment_id: str, user_id: str) -> ProjectComment:
    """
    Add a like to a comment from a user.
    If the like already exists, raise an exception.
    """
    # Fetch the comment
    comment = db.query(ProjectComment).filter(ProjectComment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Check if the user already liked the comment
    existing_like = db.query(CommentLike).filter(
        CommentLike.comment_id == comment_id,
        CommentLike.user_id == user_id
    ).first()

    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has already liked this comment",
        )

    # Create a new like entry
    like = CommentLike(comment_id=comment_id, user_id=user_id)
    db.add(like)

    try:
        db.commit()
        db.refresh(comment)  # Refresh the comment to reflect changes if needed
    except Exception as e:
        db.rollback()  # Roll back on any failure
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while liking the comment",
        ) from e

    return like.comment
