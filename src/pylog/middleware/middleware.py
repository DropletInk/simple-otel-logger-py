from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Any
import uuid
import structlog
import time
from pylog.logger import log_configure


def add_request_id() -> uuid.UUID:
    request_id = uuid.uuid4()

    structlog.contextvars.bind_contextvars(request_id=request_id)

    return request_id


log_configure()


def create_log_middleware(
    logger,
    request_data: Callable[[Any], dict[str, Any]],
    response_data: Callable[[Any, Any], dict[str, Any]],
) -> Callable[[Any, Callable[[Any], Any]], Any]:
    async def log_middleware(
        request: Any, call_next: Callable[[Any], Any]
    ) -> Any:
        start_time = time.time()
        req_data = request_data(request)
        add_request_id()

        logger.info("Request Started", attributes=req_data)

        response = await call_next(request)

        duration = time.time() - start_time
        res_data = response_data(request, response)
        logger.info(
            "Response Received", attributes=res_data, duration=duration
        )

        return response

    return log_middleware


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        logger,
        request_data: Callable[[Any], dict[str, Any]],
        response_data: Callable[[Any, Any], dict[str, Any]],
    ):
        super().__init__(app)

        self.dispatch_func = create_log_middleware(
            logger, request_data, response_data
        )

    async def dispatch(self, request, call_next):
        return await self.dispatch_func(request, call_next)
