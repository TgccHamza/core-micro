

@client_router.post("/games/{project_id}/add-comment", response_model=ProjectCommentResponse)
def create_comment_endpoint(
        project_id: str,
        req: ProjectCommentCreateRequest,
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
        db: AsyncSession = Depends(get_db_async),
):
    user_id = jwt_claims.get("uid")
    return services_create_comment.create_comment(db, project_id, user_id, req.comment_text)


@client_router.get("/games/{project_id}/comments", response_model=list[ProjectCommentResponse])
def list_comments_endpoint(
        project_id: str,
        db: AsyncSession = Depends(get_db_async),
):
    return services_list_comments.list_comments(db, project_id)


@client_router.put("/comments/{comment_id}", response_model=ProjectCommentResponse)
def update_comment_endpoint(
        comment_id: str,
        updated_data: ProjectCommentUpdateRequest,
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
        db: AsyncSession = Depends(get_db_async),
):
    user_id = jwt_claims.get("uid")
    return services_update_comment.update_comment(db, comment_id, updated_data, user_id)


@client_router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment_endpoint(
        comment_id: str,
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
        db: AsyncSession = Depends(get_db_async),
):
    user_id = jwt_claims.get("uid")
    return services_delete_comment.delete_comment(db, comment_id, user_id)


@client_router.post("/comments/{comment_id}/like", response_model=ProjectCommentResponse)
def like_comment_endpoint(comment_id: str, jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
                          db: AsyncSession = Depends(get_db_async)):
    user_id = jwt_claims.get("uid")
    return services_like_comment.like_comment(db, comment_id, user_id)


@client_router.post("/comments/{comment_id}/dislike", response_model=ProjectCommentResponse)
def dislike_comment_endpoint(comment_id: str, jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
                             db: AsyncSession = Depends(get_db_async)):
    user_id = jwt_claims.get("uid")
    return services_dislike_comment.dislike_comment(db, comment_id, user_id)
