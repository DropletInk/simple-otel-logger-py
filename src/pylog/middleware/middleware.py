import time
import uuid
from collections.abc import Callable
from typing import Any

import structlog
from starlette.middleware.base import BaseHTTPMiddleware

from pylog.logger import log_configure
from opentelemetry import context
from opentelemetry.baggage.propagation import W3CBaggagePropagator

baggage_propagator = W3CBaggagePropagator()

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
        
        extracted_context = baggage_propagator.extract(request.headers)
        context_restoration_token = context.attach(extracted_context)
        
        try:
            start_time = time.time()
            req_data = request_data(request)
            req_data["request_id"] = add_request_id()

            logger.info("Request Started", attributes=req_data)

            response = await call_next(request)

            duration = time.time() - start_time
            res_data = response_data(request, response)
            logger.info(
                "Response Received", attributes=res_data, duration=duration
            )

            return response

        finally:
            context.detach(context_restoration_token)
            
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
