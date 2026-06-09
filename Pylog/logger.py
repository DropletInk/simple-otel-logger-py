from .metrics import counter
from datetime import datetime
from functools import wraps
from typing import Any

import structlog
from opentelemetry import trace

tracer = trace.get_tracer("simple-otel-logger")
SEVERITY = {
    "DEBUG": 5,
    "INFO": 9,
    "WARN": 13,
    "ERROR": 17,
}

def get_otel_context() -> dict[str, Any]:
    span = trace.get_current_span()

    if not span:
        return {}

    ctx = span.get_span_context()

    if not ctx.is_valid:
        return {}

    return {
        "trace_id": format(ctx.trace_id, "032x"),
        "span_id": format(ctx.span_id, "016x"),
        "trace_flags": format(ctx.trace_flags, "02x"),
    }

def traced(span_name: str | None = None):

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):

            name = span_name or func.__name__

            with tracer.start_as_current_span(name):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


class Logger:
    def __init__(
        self,
        service_name: str = "app-service",
        base: dict[str, Any] | None = None,
        custom_level: str | None = None,
    ):
        self.service_name = service_name
        self.base = base or {}
        self.custom_level = custom_level

        self.logger = structlog.get_logger()

    def build_record(
        self,
        level: str,
        message: str,
        event_name: str | None = None,
        **attributes,
    ) -> dict[str, Any]:
        return {
            "resources": {
                "attributes": {
                    "service": self.service_name,
                }
            },
            "instrumentationScope": {
                "name": "simple-otel-logger",
                "version": "1.0.0",
                "schemaUrl": None,
            },
            "severityText": level,
            "severityNumber": SEVERITY.get(level, 1),
            # "message": message,
            "eventName": event_name,
            "timestamp": datetime.utcnow().isoformat(),
            **self.base,
            **get_otel_context(),
            "attributes": attributes,
        }

    def log(
        self,
        level: str,
        message: str,
        event_name: str | None = None,
        **kwargs,
    ) -> None:
        record = self.build_record(
            level=level,
            message=message,
            event_name=event_name,
            **kwargs,
        )

        getattr(self.logger, level.lower())(message, **record)

    def info(
        self,
        message: str,
        event_name: str | None = None,
        **kwargs,
    ) -> None:
        self.log("INFO", message, event_name, **kwargs)

    def error(
        self,
        message: str,
        event_name: str | None = None,
        **kwargs,
    ) -> None:
        self.log("ERROR", message, event_name, **kwargs)

    def warn(
        self,
        message: str,
        event_name: str | None = None,
        **kwargs,
    ) -> None:
        self.log("WARN", message, event_name, **kwargs)

    def debug(
        self,
        message: str,
        event_name: str | None = None,
        **kwargs,
    ) -> None:
        self.log("DEBUG", message, event_name, **kwargs)


def configure_structlog():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(indent=4),
        ]
    )


def get_logger(
    service_name: str = "app-service",
    base: dict[str, Any] | None = None,
    custom_level: str | None = None,
) -> Logger:
    configure_structlog()

    return Logger(
        service_name=service_name,
        base=base,
        custom_level=custom_level,
    )