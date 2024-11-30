# MiddlewareWrapper.py
import traceback

from fastapi.routing import APIRoute
from typing import Callable, List, Type
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse


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

                try:
                    return await handler(request)
                except Exception as exc:
                    tb_str = traceback.format_exc()  # Capture the traceback
                    return JSONResponse(
                        status_code=500,
                        content={
                            "error": str(exc),
                            "traceback": tb_str,
                            "detail": {
                                "method": request.method,
                                "url": request.url.path,
                            },
                        },
                    )

            return custom_route_handler

    return CustomAPIRoute
