from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt  # You can install with `pip install python-jose`
from typing import Optional


class ClientAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: Optional[str] = None):
        super().__init__(app)
        self.secret_key = secret_key  # Optional, only for validation (you can skip if not needed)

    async def dispatch(self, request: Request, call_next):
        # Read the Authorization header
        auth_header = request.headers.get("Authorization")
        default_claims = {
            "uid": "93ca55e0-1394-4449-9a3f-2854f37b6b1d",
            "org_id": "3be3d36b-6bee-4b1a-9c0f-11092d28c1b3",
            "orgs": [
                "ocp"
            ],
            "username": "zak2",
            "user_type": "client",
            "role": "player"
        }
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[1]
            try:
                # Decode the JWT without validation
                # You can provide `options={"verify_signature": False}` to skip verification
                claims = jwt.decode(token, key=self.secret_key or "", options={"verify_signature": False})
                # Attach claims to the request state for access in controllers
                request.state.jwt_claims = claims
            except jwt.JWTError as e:
                request.state.jwt_claims = default_claims
        else:
            request.state.jwt_claims = default_claims

        return call_next, request
