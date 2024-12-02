import httpx
import logging

logger = logging.getLogger(__name__)


class GameDBServiceClient:
    def __init__(self):
        self.base_url = 'https://dev-api.thegamechangercompany.io/api'

    async def create_game(self) -> str | None:
        url = f"{self.base_url}/create-game"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url)
                response.raise_for_status()  # Raise HTTP exceptions for 4xx/5xx responses
                if response.status_code == 200 or response.status_code == 201 or response.status_code == 202:
                    data = response.json()
                    return data.get("id", None)
                return None
        except httpx.RequestError as e:
            logger.error(f"Error connecting to mongodb service: {str(e)}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"GameDBServiceClient service error: {str(e)}")
            return None


def get_game_db_service() -> GameDBServiceClient:
    return GameDBServiceClient()
