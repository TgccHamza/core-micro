import os

import httpx
from fastapi import HTTPException

import logging
logger = logging.getLogger(__name__)


class OrganisationServiceClient:
    def __init__(self):
        self.base_url = f'{os.getenv("CLIENTAUTH_API")}/api/v1'

    async def get_organisation_name(self, organisation_code: str) -> str:
        url = f"{self.base_url}/organisations/{organisation_code}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()  # Raise HTTP exceptions for 4xx/5xx responses
                if response.status_code == 200 or response.status_code == 201 or response.status_code == 202:
                    data = response.json()
                return data.get("name", "Unknown Organisation")
        except httpx.RequestError as e:
            logger.error(f"Error connecting to organisation service: {str(e)}")
            return "Unknown Organisation"
        except httpx.HTTPStatusError as e:
            logger.error(f"Organisation service error: {response.json().get('detail', str(e))}")
            return "Unknown Organisation"

    async def get_organisation_names(self, organisation_codes: list[str]) -> dict:
        url = f"{self.base_url}/organisations/batch"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json={"organisation_codes": organisation_codes})
                response.raise_for_status()
                return response.json()  # Assume response is {"code1": "name1", "code2": "name2", ...}
        except httpx.RequestError as e:
            logger.error(f"Error connecting to organisation service: {str(e)}")
            return {}



def get_organisation_service() -> OrganisationServiceClient:
    return OrganisationServiceClient()
