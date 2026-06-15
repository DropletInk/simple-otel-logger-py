import structlog
from opentelemetry import trace
from functools import wraps
import inspect
from typing import TypedDict
from importlib.metadata import packages_distributions
from pylog.telemetry import get_tracer

tracer = trace.get_tracer("Mytracer")


class SpanInfo(TypedDict):
    trace_id: str
    span_id: str
    trace_flags: int


class EventDict(TypedDict):
    span: SpanInfo | None


def add_open_telemetry_spans(
    logger: object, method_name: str, event_dict: EventDict
) -> EventDict:
    span = trace.get_current_span()
    if not span.is_recording():
        event_dict["span"] = None
        return event_dict

    ctx = span.get_span_context()

    event_dict["span"] = {
        "trace_id": format(ctx.trace_id, "032x"),
        "span_id": format(ctx.span_id, "016x"),
        "trace_flags": int(ctx.trace_flags),
    }
    return event_dict


def otel_tags(
    logger: object, method_name: str, event_dict: EventDict
) -> EventDict:
    event_dict["instrumentationScope"] = {
        "name": "simple-otel-logger",
        "version": "1.0.0",
    }
    return event_dict


def log_organiser(
    logger: object, method_name: str, event_dict: EventDict
) -> dict:
    return {
        "resources": event_dict.get("resources"),
        "instrumentationScope": event_dict.get("instrumentationScope"),
        "timestamp": event_dict.get("timestamp"),
        "severityText": event_dict.get("severityText"),
        "severityNumber": event_dict.get("severityNumber"),
        "event": event_dict.get("event"),
        "request_id": event_dict.get("request_id"),
        "span": event_dict.get("span"),
        "attributes": event_dict.get("attributes", {}),
    }


def log_configure() -> None:
    # struture of the logs using structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_open_telemetry_spans,
            otel_tags,
            structlog.processors.add_log_level,
            rename_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(
                fmt="%Y-%m-%d %H:%M:%S", utc=False
            ),
            log_organiser,
            structlog.processors.JSONRenderer(indent=4),
        ],
    )


def rename_level(
    logger: object, method_name: str, event_dict: EventDict
) -> EventDict:
    level_mapping = {
        "DEBUG": 5,
        "INFO": 9,
        "WARNING": 13,
        "ERROR": 17,
        "CRITICAL": 21,
    }
    if "level" in event_dict:
        event_dict["severityText"] = event_dict.pop("level").upper()
        event_dict["severityNumber"] = level_mapping.get(
            event_dict["severityText"], 0
        )
    return event_dict


def traced(span_name: str | None = None):
    def decorator(func):
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def asy_wrapper(*args, **kwargs):
                name = span_name or func.__name__

                with tracer.start_as_current_span(name):
                    return await func(*args, **kwargs)

            return asy_wrapper

        @wraps(func)
        def wrapper(*args, **kwargs):
            name = span_name or func.__name__

            with tracer.start_as_current_span(name):
                return func(*args, **kwargs)

        return wrapper

    return decorator


class Logger:
    _initialized = False

    def __init__(self, service_name=packages_distributions()["pylog"][0]):
        get_tracer()
        log_configure()

        resources = {"service_name": service_name}
        instrumentationScope = {
            "name": "simple-otel-logger",
            "version": "1.0.0",
        }
        self.logger = structlog.get_logger().bind(
            resources=resources, instrumentationScope=instrumentationScope
        )

    def info(self, message, attributes=None, **kwargs):
        if attributes is not None:
            kwargs["attributes"] = attributes
        self.logger.info(message, **kwargs)

    def error(self, message, attributes=None, **kwargs):
        if attributes is not None:
            kwargs["attributes"] = attributes
        self.logger.error(message, **kwargs)

    def warning(self, message, attributes=None, **kwargs):
        if attributes is not None:
            kwargs["attributes"] = attributes
        self.logger.warning(message, **kwargs)

    def debug(self, message, attributes=None, **kwargs):
        if attributes is not None:
            kwargs["attributes"] = attributes
        self.logger.debug(message, **kwargs)
