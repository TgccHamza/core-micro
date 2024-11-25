from typing import Any

import httpx
from fastapi import HTTPException

from app.logger import logger


class UserServiceClient:
    def __init__(self):
        self.base_url = 'https://dev-api.thegamechangercompany.io/client-auth/api/v1'

    async def get_user_by_email(self, email: str) -> Any | None:
        url = f"{self.base_url}/users/email/{email}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()  # Raise HTTP exceptions for 4xx/5xx responses
                if response.status_code == 200 or response.status_code == 201 or response.status_code == 202:
                    data = response.json()
                return data
        except httpx.RequestError as e:
            logger.error(f"Error connecting to organisation service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to organisation service: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Organisation service error: {response.json().get('detail', str(e))}")
            return None

    async def get_user_by_id(self, code: str) -> Any | None:
        url = f"{self.base_url}/users/{code}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()  # Raise HTTP exceptions for 4xx/5xx responses
                if response.status_code == 200 or response.status_code == 201 or response.status_code == 202:
                    data = response.json()
                return data
        except httpx.RequestError as e:
            logger.error(f"Error connecting to organisation service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to organisation service: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Organisation service error: {response.json().get('detail', str(e))}")
            return None