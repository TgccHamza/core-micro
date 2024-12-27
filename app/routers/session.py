


# ---------------- Session Routes ----------------

@router.post("/sessions", response_model=SessionCreateResponse)
async def create_session(session: SessionCreateRequest, db: AsyncSession = Depends(get_db_async),
                         jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        return await services_create_session.create_session(db, session, org_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")



@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db_async), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        sessions = await services_get_sessions.get_sessions(db, org_id)
        return sessions
    except Exception as e:
        # General error handling for unexpected issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db_async),
                      jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        session = await services_show_session.show_session(db, session_id, org_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        # General error handling for unexpected issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while get the session: {str(e)}"
        )


@router.put("/sessions/{session_id}/config", response_model=SessionCreateResponse)
def config_session(session_id: str, session: SessionConfigRequest, db: AsyncSession = Depends(get_db_async),
                   jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    try:
        org_id = jwt_claims.get("org_id")
        try:
            return services_config_session.config_session(db, session_id, session, org_id)
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Session not found")

    except Exception as e:
        # General error handling for unexpected issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while config the session: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db_async),
                         jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    """
    Deletes a session by its ID. Ensures the session exists and belongs to the correct organization.
    """
    org_id = jwt_claims.get("org_id")

    try:
        # Delegate the session deletion logic to the service layer
        await services_delete_session.delete_session(db, session_id, org_id)
        return {"message": "Session deleted successfully."}

    except NoResultFoundError:
        # Specific exception when the session is not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found."
        )
    except Exception as e:
        # General error handling for unexpected issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the session: {str(e)}"
        )


@router.post("/sessions/{session_id}/assign-moderator", response_model=dict)
async def assign_moderator(session_id: str, background_tasks: BackgroundTasks, req: AssignModeratorRequest,
                           db: AsyncSession = Depends(get_db_async),
                           jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")

    # Call the service to handle player invitations
    await services_assign_moderator.assign_moderator(db, session_id, org_id, req.email, background_tasks)

    return {"message": "Invitations sent successfully"}


@router.post("/sessions/{session_id}/invite-players", response_model=InvitePlayerResponse)
async def invite_players(
        session_id: str,
        background_tasks: BackgroundTasks,
        invite_req: InvitePlayerRequest,
        db: AsyncSession = Depends(get_db_async),
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)
):
    org_id = jwt_claims.get("org_id")

    # Perform session validation before processing
    session = await get_session_by_id(session_id, org_id, db)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Arena session with ID {session_id} not found."
        )

    # Call the service to handle player invitations
    await services_invite_players.invite_players(db, session, invite_req, background_tasks)

    return {"message": "Invitations sent successfully"}


@router.post("/sessions/player/{session_player_id}/remove")
async def remove_player(session_player_id: str, db: AsyncSession = Depends(get_db_async),
                        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    """
    Removes a player from the specified session.
    Ensures the player exists and belongs to the correct organization.
    """
    org_id = jwt_claims.get("org_id")

    try:
        # Delegate session validation and removal to the service layer
        await services_remove_player_from_session.remove_player_from_session(db, session_player_id, org_id)
        return {"message": "Player removed from session successfully."}

    except PlayerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session Player with ID {session_player_id} not found."
        )
    except Exception as e:
        # Handle any unforeseen errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while removing the player: {str(e)}"
        )
