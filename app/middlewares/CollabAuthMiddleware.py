from fastapi import Request

from starlette.middleware.base import BaseHTTPMiddleware


class CollabAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"Incoming request: {request.method} {request.url}")

        return call_next, request