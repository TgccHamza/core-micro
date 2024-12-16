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
            user = users.get(player.user_id, None)
            items.append(
                GameSessionPlayerResponse(
                    user_id=player.user_id,
                    role=f"{ 'game_master' if player.is_game_master else 'player'}",
                    email=user.get('email') if user else None,
                    first_name=user.get('first_name') if user else None,
                    last_name=user.get('last_name') if user else None,
                    picture=user.get('picture') if user else None,
                    is_game_master=player.is_game_master,
                    is_moderator=False,
                    is_player=not player.is_game_master,
                )
            )
        if session and session.super_game_master_id:
            user = users.get(session.super_game_master_id, None)
            items.append(
                GameSessionPlayerResponse(
                    user_id=session.super_game_master_id,
                    role=f"moderator",
                    email=user.get('email') if user else None,
                    first_name=user.get('first_name') if user else None,
                    last_name=user.get('last_name') if user else None,
                    picture=user.get('picture') if user else None,
                    is_game_master=False,
                    is_moderator=True,
                    is_player=False,
                )
            )

        return items
    return []
