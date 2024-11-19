from fastapi import Request
from typing import Dict, Any


async def get_jwt_claims(request: Request) -> Dict[Any, Any]:
    if request.state and "jwt_claims" in request.state.__dict__['_state']:
        return request.state.jwt_claims
    else:
        return {
            "uid": "93ca55e0-1394-4449-9a3f-2854f37b6b1d",
            "org_id": "3be3d36b-6bee-4b1a-9c0f-11092d28c1b3",
            "orgs": [
                "ocp"
            ],
            "username": "zak2",
            "user_type": "client",
            "role": "player"
        }