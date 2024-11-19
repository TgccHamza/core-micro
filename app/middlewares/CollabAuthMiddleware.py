from fastapi import Request

from starlette.middleware.base import BaseHTTPMiddleware


class CollabAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"Incoming request: {request.method} {request.url}")
        print("body request")
        body = await request.body()
        print("Request body:", body[1:200])  # Log request body

        return call_next, request