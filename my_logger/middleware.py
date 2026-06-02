import time

from fastapi import Request

from .context import bind_request_context, clear_request_context
from .logger import get_logger
from .metrics import ACTIVE_REQUESTS, ERROR_COUNT, REQUEST_COUNT, REQUEST_LATENCY

log = get_logger()


async def logging_middleware(request: Request, call_next):

    ACTIVE_REQUESTS.inc()

    start_time = time.time()

    bind_request_context()

    try:
        log.info("request_started", method=request.method, path=request.url.path)

        response = await call_next(request)

        duration = time.time() - start_time

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method, endpoint=request.url.path
        ).observe(duration)

        log.info(
            "request_completed",
            status_code=response.status_code,
            duration=round(duration, 4),
        )

        return response

    except Exception:
        ERROR_COUNT.labels(method=request.method, endpoint=request.url.path).inc()

        log.exception("request_failed")

        raise

    finally:
        ACTIVE_REQUESTS.dec()

        clear_request_context()
