# MiddlewareWrapper.py
import logging
import traceback

from fastapi.routing import APIRoute
from typing import Callable, List, Type
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from app.exceptions.base_exception import CoreBaseException
from app.payloads.response.SuccessResponse import SuccessResponse

logger = logging.getLogger(__name__)


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
                    data = await handler(request)
                    if isinstance(data, SuccessResponse):
                        return JSONResponse(
                            status_code=data.status_code,
                            content=data.serialize(),
                        )
                    else:
                        return data
                except CoreBaseException as core_ex:
                    # If the status code is 200, log the message but don't return an error
                    if 100 <= core_ex.status_code <= 199:
                        logger.info(
                            f"{core_ex.status_code} ==> {request.url.path}: Request processed successfully: {core_ex.message}")
                    elif 200 <= core_ex.status_code <= 299:
                        logger.log(
                            f"{core_ex.status_code} ==> {request.url.path}: Request processed successfully: {core_ex.message}")
                    elif 400 <= core_ex.status_code <= 499:
                        # For non-success status codes, log the traceback
                        tb_str = traceback.format_exc()
                        logger.warning(
                            f"{core_ex.status_code} ===> {request.url.path}: ClientCoreBaseException {core_ex.message} traceback: {tb_str}")
                    elif 500 <= core_ex.status_code <= 599:
                        # For non-success status codes, log the traceback
                        tb_str = traceback.format_exc()
                        logger.error(
                            f"{core_ex.status_code} ===> {request.url.path}: ServerCoreBaseException {core_ex.message} traceback: {tb_str}")

                    return JSONResponse(
                        status_code=core_ex.status_code,
                        content=core_ex.serialize(),
                    )
                except Exception as exc:
                    tb_str = traceback.format_exc()
                    logger.error(
                        f"500 ===> {request.url.path}: ServerCoreBaseException {str(exc)} traceback: {tb_str}")

                    return JSONResponse(
                        status_code=500,
                        content={
                            "success": False,
                            "message": "An unexpected error occurred",
                            "data": None,
                            "error": "Internal Server Error",
                        },
                    )

            return custom_route_handler

    return CustomAPIRoute
