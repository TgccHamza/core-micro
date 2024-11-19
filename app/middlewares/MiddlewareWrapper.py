# MiddlewareWrapper.py
from fastapi.routing import APIRoute
from typing import Callable, List, Type
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


def middlewareWrapper(middlewares: List[BaseHTTPMiddleware] = []) -> Type[APIRoute]:
    class CustomAPIRoute(APIRoute):
        def get_route_handler(self) -> Callable:
            original_route_handler = super().get_route_handler()

            async def custom_route_handler(request: Request) -> Response:
                # Apply middleware in reverse order
                handler = original_route_handler
                for current_middleware in reversed(middlewares):
                    middleware_instance = current_middleware(self.app)
                    handler, request = await middleware_instance.dispatch(request=request, call_next=handler)

                body = await request.body()
                print("Request body 2:", body[1:200])  # Log request body
                return await handler(request)

            return custom_route_handler

    return CustomAPIRoute
