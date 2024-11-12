from fastapi import Request

from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"Incoming request: {request.method} {request.url}")

        # Process the request
        response = await call_next(request)

        # After processing
        print(f"Response status: {response.status_code}")

        return response