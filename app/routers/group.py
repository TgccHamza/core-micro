from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from app.middlewares.ClientAuthMiddleware import ClientAuthMiddleware
from app.middlewares.MiddlewareWrapper import middlewareWrapper

from sqlalchemy.ext.asyncio import AsyncSession
from app.helpers import get_jwt_claims
from typing import Dict, Any, List
from uuid import UUID
from app.database import get_db_async

import logging

from app.exceptions.validation_error_exception import ValidationErrorException


from app.payloads.request.GroupCreateRequest import GroupCreateRequest
from app.payloads.request.GroupInviteManagerRequest import GroupInviteManagerRequest
from app.payloads.request.GroupUpdateRequest import GroupUpdateRequest


from app.payloads.response.AssignGameToGroupResponse import AssignGameToGroupResponse
from app.payloads.response.AssignManagerToGroupByEmailResponse import AssignManagerToGroupByEmailResponse
from app.payloads.response.DeleteGroupResponse import DeleteGroupResponse
from app.payloads.response.GroupClientResponse import GroupClientResponse
from app.payloads.response.GroupCreateClientResponse import GroupCreateClientResponse
from app.payloads.response.GroupListClientResponse import GroupListClientResponse
from app.payloads.response.GroupLiteClientResponse import GroupLiteClientResponse
from app.payloads.response.RemoveGameFromGroupResponse import RemoveGameFromGroupResponse
from app.payloads.response.InviteManagerResponse import InviteManagerResponse
from app.payloads.response.RemoveManagerFromGroupByIdResponse import RemoveManagerFromGroupByIdResponse

from app.services.assign_game_to_group import assign_game_to_group
from app.services.assign_manager_to_group_by_email import assign_manager_to_group_by_email
from app.services.remove_game_from_group import remove_game_from_group
from app.services.remove_manager_from_group_by_email import remove_manager_from_group_by_email
from app.services.remove_manager_from_group_by_id import remove_manager_from_group_by_id
from app.services import invite_managers as services_invite_managers
from app.services import create_group as services_create_group
from app.services import get_groups as services_get_groups
from app.services import update_group as services_update_group
from app.services import delete_group as services_delete_group
from app.services import show_group as services_show_group

from app.payloads.response.SuccessResponse import SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    route_class=middlewareWrapper(middlewares=[ClientAuthMiddleware])
)


# ---------------- Group Routes ----------------

@router.post("/groups", response_model=SuccessResponse[GroupCreateClientResponse])
async def create_group(group: GroupCreateRequest,
                       background_tasks: BackgroundTasks,
                       db: AsyncSession = Depends(get_db_async),
                       jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    response = await services_create_group.create_group(db, group, org_id, background_tasks)
    return SuccessResponse[GroupCreateClientResponse](data=response)


@router.get("/groups", response_model=SuccessResponse[List[GroupListClientResponse]])
async def list_groups(db: AsyncSession = Depends(get_db_async), jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    response = await services_get_groups.get_groups(db, org_id)
    data = SuccessResponse[List[GroupListClientResponse]](data=response)
    return data


@router.get("/groups/{group_id}", response_model=SuccessResponse[GroupClientResponse])
async def show_group(group_id: str, db: AsyncSession = Depends(get_db_async),
                    jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")

    group = await services_show_group.show_group(db, group_id, org_id)

    return SuccessResponse[GroupClientResponse](data=group)


@router.post("/groups/{group_id}/assign-game/{game_id}", response_model=SuccessResponse[AssignGameToGroupResponse])
async def associate_project_to_group(group_id: UUID, game_id: UUID, db: AsyncSession = Depends(get_db_async),
                                     jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    # make the service code here

    if not org_id:
        raise ValidationErrorException(error="Organization ID missing from JWT claims")
    response = await assign_game_to_group(group_id=str(group_id), game_id=str(game_id), organisation_id=org_id, db=db)

    return SuccessResponse[AssignGameToGroupResponse](data=response)


@router.delete("/groups/{group_id}/remove-game/{game_id}")
async def disassociate_project_in_group(group_id: UUID, game_id: UUID, db: AsyncSession = Depends(get_db_async),
                                        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    if not org_id:
        raise ValidationErrorException(error="Organization ID missing from JWT claims")

    # replace this with good things return await remove_game_from_group(group_id=str(group_id), game_id=str(game_id), organisation_id=org_id, db=db)
    response = await remove_game_from_group(group_id=str(group_id), game_id=str(game_id), organisation_id=org_id, db=db)
    return SuccessResponse[RemoveGameFromGroupResponse](data=response)


@router.put("/groups/{group_id}", response_model=SuccessResponse[GroupLiteClientResponse])
async def update_group(group_id: str, group: GroupUpdateRequest, db: AsyncSession = Depends(get_db_async),
                       jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    response = await services_update_group.update_group(db, group_id, group, org_id)
    return SuccessResponse[GroupLiteClientResponse](data=response)


@router.delete("/groups/{group_id}")
async def delete_group(group_id: str, db: AsyncSession = Depends(get_db_async),
                       jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    response = await services_delete_group.delete_group(db, group_id, org_id)
    return SuccessResponse[DeleteGroupResponse](data=response)


@router.post("/groups/{group_id}/invite-managers", response_model=SuccessResponse[InviteManagerResponse])
async def invite_manager(
        group_id: str,
        background_tasks: BackgroundTasks,
        invite_req: GroupInviteManagerRequest,
        db: AsyncSession = Depends(get_db_async),
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)
):
    org_id = jwt_claims.get("org_id")
    await services_invite_managers.invite_managers(db, group_id, org_id, invite_req.managers, background_tasks)
    return SuccessResponse[InviteManagerResponse](data=InviteManagerResponse(message="Invitations sent successfully"))

@router.post("/groups/manager/{group_manager_id}/remove", response_model=SuccessResponse[RemoveManagerFromGroupByIdResponse])
async def remove_manager(group_manager_id: str, db: AsyncSession = Depends(get_db_async),
                         jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):

    response = await remove_manager_from_group_by_id(group_manager_id, db)

    return SuccessResponse[RemoveManagerFromGroupByIdResponse](data=response)


@router.post("/groups/{group_id}/assign-manager-by-email/{manager_email}")
async def associate_manager_to_group(group_id: UUID,
                                     manager_email: str,
                                     db: AsyncSession = Depends(get_db_async),
                                     jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    if not org_id:
        raise ValidationErrorException(error="Organization ID missing from JWT")
    response = await assign_manager_to_group_by_email(group_id=str(group_id), manager_email=manager_email,
                                                      organisation_id=org_id, db=db)
    return SuccessResponse[AssignManagerToGroupByEmailResponse](data=response)


@router.delete("/groups/{group_id}/remove-manager-by-email/{manager_email}")
async def disassociate_manager_from_group(group_id: UUID,
                                          manager_email: str,
                                          db: AsyncSession = Depends(get_db_async),
                                          jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)):
    org_id = jwt_claims.get("org_id")
    if not org_id:
        raise ValidationErrorException(error="Organization ID missing from JWT")
    response = await remove_manager_from_group_by_email(group_id=str(group_id), manager_email=manager_email,
                                                        organisation_id=org_id, db=db)
    return SuccessResponse[RemoveGameFromGroupResponse](data=response)





@router.get("/groups/game/{game_id}", response_model=List[GroupByGameResponse])
async def groups_by_game(
        game_id: str,
        db: AsyncSession = Depends(get_db_async),
        jwt_claims: Dict[Any, Any] = Depends(get_jwt_claims)
):
    """
    Endpoint to retrieve groups by game.

    This endpoint fetches the groups related to a specific game, ensuring that the game
    belongs to the organization of the current user. It calls the `groups_by_game`
    service to retrieve the group details.

    Parameters:
    - game_id (str): The ID of the game.
    - db (Session): The database session, injected through dependency.
    - jwt_claims (Dict): The JWT claims containing organization info.

    Returns:
    - List[GroupByGameResponse]: A list of groups associated with the game.

    Raises:
    - HTTPException: If the game is not found or does not belong to the user's organization.
    """
    try:
        org_id = jwt_claims.get("org_id")

        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization ID missing in JWT claims."
            )

        # Call the service to get groups related to the game
        groups = await services_groups_by_game.groups_by_game(db, game_id, org_id)

        if not groups:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No groups found for the game with ID {game_id}."
            )

        return groups

    except Exception as e:
        # Log the error (you can use a logger like 'logging' or any other framework)
        logger.error(f"Error in groups_by_game: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request {e}"
        )
