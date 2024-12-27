import os
from typing import Any

import httpx
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)
from app.payloads.response.UserResponse import UserResponse


class UserServiceClient:
    def __init__(self):
        self.base_url = f'{os.getenv("CLIENTAUTH_API")}/api/v1'

    async def get_user_by_email(self, email: str) -> UserResponse | None:
        url = f"{self.base_url}/users/email/{email}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()  # Raise HTTP exceptions for 4xx/5xx responses
                if response.status_code >= 200 or response.status_code <= 299:
                    data = response.json()
                    full_name = data.get("name",
                                         "").strip()  # Ensure we handle empty or invalid full_name gracefully
                    if " " in full_name:
                        first_name, last_name = full_name.split(" ", 1)  # Split only on the first space
                    else:
                        first_name = full_name  # If only one name is provided, treat it as the first name
                        last_name = None  # No last name in this case

                    return UserResponse(
                        user_id=data.get("user_id", None),
                        email=data.get("email", None),
                        user_email=data.get("email", None),
                        username=data.get("username", None),
                        full_name=full_name,
                        user_name=full_name,  # Still use full_name here
                        first_name=first_name,
                        last_name=last_name,
                    )
                return None
        except httpx.RequestError as e:
            logger.error(f"Error connecting to user service: {str(e)}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"User service error: {response.json().get('detail', str(e))}")
            return None

    async def get_users_by_email(self, emails: list[str]) -> dict[str, UserResponse]:
        items = dict()
        url = f"{self.base_url}/users/bulk/emails"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json={'email': emails})
                response.raise_for_status()  # Raise HTTP exceptions for 4xx/5xx responses
                if response.status_code >= 200 or response.status_code <= 299:
                    data = response.json()
                    users = data.get("users", [])  # Ensure we handle empty or invalid users gracefully
                    for user in users:
                        full_name = user.get("name",
                                             "").strip()  # Ensure we handle empty or invalid full_name gracefully
                        if " " in full_name:
                            first_name, last_name = full_name.split(" ", 1)  # Split only on the first space
                        else:
                            first_name = full_name  # If only one name is provided, treat it as the first name
                            last_name = None  # No last name in this case

                        items[user.get('email')] = UserResponse(
                            user_id=user.get("user_id", None),
                            email=user.get("email", None),
                            user_email=user.get("email", None),
                            username=user.get("username", None),
                            full_name=full_name,
                            user_name=full_name,  # Still use full_name here
                            first_name=first_name,
                            last_name=last_name)
                return items
        except httpx.RequestError as e:
            logger.error(f"Error connecting to user service: {str(e)}")
            return items
        except httpx.HTTPStatusError as e:
            logger.error(f"User service error: {response.json().get('detail', str(e))}")
            return items

    async def get_users_by_id(self, ids: list[str]) -> dict[str, UserResponse]:
        items = dict()
        url = f"{self.base_url}/users/bulk/ids"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json={'user_id': ids})
                response.raise_for_status()  # Raise HTTP exceptions for 4xx/5xx responses
                if response.status_code >= 200 or response.status_code <= 299:
                    data = response.json()
                    users = data.get("users", [])  # Ensure we handle empty or invalid users gracefully
                    for user in users:
                        first_name = user.get("first_name", "")  # If only one name is provided, treat it as the first name
                        last_name = user.get("last_name", "")  # No last name in this case

                        items[user.get('user_id')] = UserResponse(
                            user_id=user.get("user_id", None),
                            email=user.get("email", None),
                            user_email=user.get("email", None),
                            username=user.get("username", None),
                            full_name=f"{first_name} {last_name}".strip(),
                            user_name=f"{first_name} {last_name}".strip(),  # Still use full_name here
                            first_name=first_name,
                            last_name=last_name)
                return items
        except httpx.RequestError as e:
            logger.error(f"Error connecting to user service: {str(e)}")
            return items
        except httpx.HTTPStatusError as e:
            logger.error(f"User service error: {response.json().get('detail', str(e))}")
            return items

    async def get_user_by_id(self, code: str) -> UserResponse | None:
        url = f"{self.base_url}/users/{code}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()  # Raise HTTP exceptions for 4xx/5xx responses
                if response.status_code >= 200 or response.status_code <= 299:
                    data = response.json()

                    full_name = data.get("name",
                                         "").strip()  # Ensure we handle empty or invalid full_name gracefully
                    if " " in full_name:
                        first_name, last_name = full_name.split(" ", 1)  # Split only on the first space
                    else:
                        first_name = full_name  # If only one name is provided, treat it as the first name
                        last_name = None  # No last name in this case

                    return UserResponse(
                        user_id=data.get("user_id"),
                        email=data.get("email", None),
                        user_email=data.get("email"),
                        username=data.get("username"),
                        full_name=full_name,
                        user_name=full_name,  # Still use full_name here
                        first_name=first_name,
                        last_name=last_name,
                    )
                return None
        except httpx.RequestError as e:
            logger.error(f"Error connecting to user service: {str(e)}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"User service error: {str(e)}")
            return None


def get_user_service() -> UserServiceClient:
    return UserServiceClient()
