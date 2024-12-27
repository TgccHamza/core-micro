
client_router = APIRouter(
    route_class=middlewareWrapper(middlewares=[ClientAuthMiddleware])
)


@client_router.get("/espace-admin", response_model=AdminSpaceClientResponse)
async def admin_space(
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
        db: AsyncSession = Depends(get_db_async)
):
    """
    Endpoint to retrieve admin space information for a client.

    This endpoint fetches the admin space details for the client based on JWT claims,
    which include the organization ID (org_id) and user ID (uid). It calls the `espaceAdmin`
    service to retrieve the necessary data from the database.

    Parameters:
    - jwt_claims (Dict): The JWT claims, which include the `org_id` and `uid`.
    - db (AsyncSession): The database AsyncSession, injected through dependency.

    Returns:
    - AdminSpaceClientResponse: The response model containing admin space details.

    Raises:
    - HTTPException: If `org_id` or `uid` is missing from the JWT claims or if a database error occurs.
    """
    try:
        org_id = jwt_claims.get("org_id")
        user_id = jwt_claims.get("uid")
        #user_email = jwt_claims.get("email")
        role = jwt_claims.get("role")

        if not org_id or not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing 'org_id' or 'uid' in JWT claims"
            )
        if role == "admin":
            # Call the service function to retrieve the admin space data
            admin_space_data = await services_space_admin.space_admin(db=db, user_id=user_id, org_id=org_id)
        else:
            admin_space_data = await services_space_user.space_user(db=db, user_id=user_id,
                                                                    org_id=org_id)

        if admin_space_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin space data not found"
            )

        return admin_space_data

    except Exception as e:
        # Log the error (you can use a proper logging framework in your project)
        logger.error(f"Error in admin_space: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request {e}"
        )


@client_router.get("/game-view/{game_id}", response_model=GameViewClientResponse|GameViewModeratorClientResponse|GameViewPlayerClientResponse)
async def game_view(game_id: str, jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
                    db: AsyncSession = Depends(get_db_async)):
    try:
        org_id = jwt_claims.get("org_id")
        user_id = jwt_claims.get("uid")
        # email = jwt_claims.get("email")
        role = jwt_claims.get("role")
        if role == "admin":
            return await services_game_view.gameView(db=db, org_id=org_id, game_id=game_id)
        else:
            return await services_game_view_user.gameViewUser(db=db, org_id=org_id, user_id=user_id, game_id=game_id)
    except Exception as e:
        # Log the error (you can use a proper logging framework in your project)
        logger.error(f"Error in game_view: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request {e}"
        )


@client_router.post("/game/{project_id}/favorite", response_model=FavoriteResponse)
async def favorite_project(project_id: str, jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
                     db: AsyncSession = Depends(get_db_async)):
    """Endpoint to add a project to favorites."""

    user_id = jwt_claims.get("uid")
    return await services_favorite_project.favorite_project(db=db, user_id=user_id, project_id=project_id)


@client_router.delete("/game/{project_id}/favorite")
async def unfavorite_project(project_id: str, jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
                       db: AsyncSession = Depends(get_db_async)):
    """Endpoint to remove a project from favorites."""

    user_id = jwt_claims.get("uid")

    return await services_unfavorite_project.unfavorite_project(db=db, user_id=user_id, project_id=project_id)


@client_router.get("/users/{user_id}/favorites", response_model=list[ProjectClientWebResponse])
def list_favorites(jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims), db: AsyncSession = Depends(get_db_async)):
    """Endpoint to list all favorite projects of a user."""
    user_id = jwt_claims.get("uid")
    return services_list_favorites.list_favorites(db=db, user_id=user_id)


@client_router.get("/game/{game_id}/config", response_model=GameConfigResponse)
async def config_game(game_id: str, jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
                      db: AsyncSession = Depends(get_db_async)):
    """
    Endpoint to get the game configuration.
    """
    org_id = jwt_claims.get("org_id")

    if not org_id:
        raise HTTPException(status_code=401, detail="Unauthorized: Missing org ID in JWT claims.")

    config_project = await services_config_client_game.config_client_game(db=db, org_id=org_id, project_id=game_id)

    if not config_project:
        raise HTTPException(status_code=404, detail="Game not found or could not be updated.")

    return config_project


@client_router.put("/game/{game_id}", response_model=GameConfigResponse)
def update_game(
        game_id: str,
        update_data: GameUpdateRequest,
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims),
        db: AsyncSession = Depends(get_db_async),
):
    """
    Endpoint to update a game project.
    """
    org_id = jwt_claims.get("org_id")

    if not org_id:
        raise HTTPException(status_code=401, detail="Unauthorized: Missing org ID in JWT claims.")

    updated_project = services_update_client_game.update_client_game(db=db, org_id=org_id, project_id=game_id,
                                                                     update_data=update_data)

    if not updated_project:
        raise HTTPException(status_code=404, detail="Game not found or could not be updated.")

    return updated_project
