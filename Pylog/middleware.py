import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware

from .logger import get_otel_context


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        logger,
        environment: str = "development",
        request_data: Callable | None = None,
        response_data: Callable | None = None,
    ):
        super().__init__(app)

        self.logger = logger
        self.environment = environment
        self.request_data = request_data
        self.response_data = response_data

    async def dispatch(
        self,
        request,
        call_next,
    ):
        header_request_id = request.headers.get("x-request-id")

        otel_context = get_otel_context()

        request_id = header_request_id or otel_context.get("trace_id") or str(uuid.uuid4())

        start_time = time.time()

        request_payload = self.request_data(request) if self.request_data else {}

        self.logger.info(
            "HTTP request received",
            event_name="HTTP request Attempt",
            request_id=request_id,
            environment=self.environment,
            **request_payload,
        )

        response = await call_next(request)

        duration = round(time.time() - start_time, 4)

        if response.status_code >= 500:
            self.logger.error(
                "HTTP error response",
                event_name="HTTP request Error",
                request_id=request_id,
                status_code=response.status_code,
            )

        response_payload = self.response_data(request, response) if self.response_data else {}

        self.logger.info(
            "HTTP response sent",
            event_name="HTTP request Success",
            request_id=request_id,
            environment=self.environment,
            duration=duration,
            **response_payload,
        )

        return response
