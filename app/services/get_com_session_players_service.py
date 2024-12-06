from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.payloads.response.GameSessionPlayerResponse import GameSessionPlayerResponse
from app.repositories.get_players_by_session_db_index_only import get_players_by_session_db_index_only
from app.repositories.get_session_by_db_index_only import get_session_by_db_index_only
from app.services.user_service import get_user_service


async def get_com_session_players_service(db_index: str, db: AsyncSession) -> list[GameSessionPlayerResponse]:
    """Service to fetch session players and their details."""
    players = await get_players_by_session_db_index_only(db_index, db)
    if players:
        ids = [player.user_id for player in players]

        session = await get_session_by_db_index_only(db_index, db)
        if session and session.super_game_master_id:
            ids.append(session.super_game_master_id)

        if len(ids) != 0:
            users = await get_user_service().get_users_by_id(list(ids))
        else:
            users = []
        items = []
        # Transforming players and users into response objects
        for player in players:
            user = users[player.user_id]
            items.append(
                GameSessionPlayerResponse(
                    user_id=player.user_id,
                    email=user.email if user else None,
                    first_name=user.first_name if user else None,
                    last_name=user.last_name if user else None,
                    picture=user.picture if user else None,
                    is_game_master=user.is_game_master if user else False,
                    is_moderator=False,
                    is_player=not user.is_game_master if user else False,
                )
            )
        if session and session.super_game_master_id:
            user = users[session.super_game_master_id]
            items.append(
                GameSessionPlayerResponse(
                    user_id=session.super_game_master_id,
                    email=user.email if user else None,
                    first_name=user.first_name if user else None,
                    last_name=user.last_name if user else None,
                    picture=user.picture if user else None,
                    is_game_master=user.is_game_master if user else False,
                    is_moderator=False,
                    is_player=not user.is_game_master if user else False,
                )
            )

        return items
    return []
