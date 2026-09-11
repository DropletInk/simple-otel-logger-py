import inspect
import json
import logging
import sys
from functools import wraps
from typing import Any, Protocol, TypedDict, runtime_checkable

import structlog
from opentelemetry import trace
from rich.console import Console
from rich.text import Text
from structlog.typing import EventDict

from pylog.setting import get_environment
from pylog.setting.setting import get_console_enabled
from pylog.telemetry import get_tracer

tracer = trace.get_tracer(__name__)
console = Console(
    force_terminal=True,
    color_system="standard",
)


@runtime_checkable
class Logger(Protocol):
    def info(
        self,
        message: str,
        attributes: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        pass

    def error(
        self,
        message: str,
        attributes: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        pass

    def warning(
        self,
        message: str,
        attributes: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        pass

    def debug(
        self,
        message: str,
        attributes: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        pass

    def exception(
        self,
        message: str,
        attributes: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        pass


class SpanInfo(TypedDict):
    trace_id: str
    span_id: str
    trace_flags: int


def add_open_telemetry_spans(
    _logger, method_name: str | None, event_dict: EventDict
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
    _logger, method_name: str | None, event_dict: EventDict
) -> EventDict:
    event_dict["instrumentationScope"] = {
        "name": "pylog",
        "version": "1.0.0",
    }
    return event_dict


def log_organiser(
    _logger, method_name: str | None, event_dict: EventDict
) -> dict:
    return {
        "resources": event_dict.get("resources"),
        "instrumentationScope": event_dict.get("instrumentationScope"),
        # "request_id": event_dict.get("request_id"),
        "timestamp": event_dict.get("timestamp"),
        "span": event_dict.get("span"),
        "severityText": event_dict.get("severityText"),
        "severityNumber": event_dict.get("severityNumber"),
        "eventName": event_dict.get("eventName"),
        "body": event_dict.get("body"),
        "attributes": event_dict.get("attributes", {}),
    }


def discard_renderer(logger, method_name, event_dict):
    return ""


def json_renderer(logger, method_name, event_dict):
    return json.dumps(
        event_dict,
        default=str,
        separators=(",", ":"),
    )


def rich_renderer(logger, method_name, event_dict):
    severity = event_dict.get("severityText", "INFO")

    severity_styles = {
        "DEBUG": "blue",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
    }

    style = severity_styles.get(severity, "white")

    json_str = json.dumps(
        event_dict,
        indent=4,
        default=str,
    )

    text = Text(json_str)

    marker = f'"severityText": "{severity}"'

    start = text.plain.find(marker)

    if start != -1:
        value_start = start + len('"severityText": "')
        value_end = value_start + len(severity)

        text.stylize(
            f"bold {style}",
            value_start,
            value_end,
        )

    body = event_dict.get("body")

    if body is not None:
        body_marker = f'"body": "{body}"'
        start = text.plain.find(body_marker)

        if start != -1:
            text.stylize(
                f"bold {'blue'}",
                start,
                start + len(body_marker),
            )
    console.print(text, markup=False)

    return ""


def log_configure() -> None:
    processors = [
        structlog.contextvars.merge_contextvars,
        add_open_telemetry_spans,
        otel_tags,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(
            fmt="%Y-%m-%d %H:%M:%S",
            utc=False,
        ),
        rename_level,
        log_organiser,
    ]

    environment = get_environment()
    console_enabled = get_console_enabled()

    if console_enabled and environment == "development":
        processors.append(rich_renderer)
    else:
        processors.append(json_renderer)

    pylog_logger = logging.getLogger("pylog")

    pylog_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))

    pylog_logger.addHandler(handler)
    pylog_logger.setLevel(logging.DEBUG)

    pylog_logger.propagate = False

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=False,
    )


def rename_level(
    _logger, method_name: str | None, event_dict: EventDict
) -> EventDict:
    level_mapping = {
        "DEBUG": 5,
        "INFO": 9,
        "WARNING": 13,
        "ERROR": 17,
    }
    if "level" in event_dict:
        event_dict["severityText"] = str(event_dict.pop("level")).upper()
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


class ConsoleLogger:
    def __init__(self, service_name: str = "Unknown-Service"):
        get_tracer()
        log_configure()
        self.service_name = service_name

        resources = {
            "service_name": self.service_name,
            "environment": get_environment(),
        }

        self.logger = structlog.get_logger("pylog").bind(resources=resources)

    def info(self, message, eventName=None, attributes=None, **kwargs):
        kwargs["body"] = message
        if eventName is not None:
            kwargs["eventName"] = eventName
        if attributes is not None:
            kwargs["attributes"] = attributes
        self.logger.info(message, **kwargs)

    def error(self, message, eventName=None, attributes=None, **kwargs):
        kwargs["body"] = message
        if eventName is not None:
            kwargs["eventName"] = eventName
        if attributes is not None:
            kwargs["attributes"] = attributes
        self.logger.error(message, **kwargs)

    def warning(self, message, eventName=None, attributes=None, **kwargs):
        kwargs["body"] = message
        if eventName is not None:
            kwargs["eventName"] = eventName
        if attributes is not None:
            kwargs["attributes"] = attributes
        self.logger.warning(message, **kwargs)

    def debug(self, message, eventName=None, attributes=None, **kwargs):
        kwargs["body"] = message
        if eventName is not None:
            kwargs["eventName"] = eventName
        if attributes is not None:
            kwargs["attributes"] = attributes
        self.logger.debug(message, **kwargs)

    def exception(self, message, eventName=None, attributes=None, **kwargs):
        kwargs["body"] = message
        if eventName is not None:
            kwargs["eventName"] = eventName
        if attributes is not None:
            kwargs["attributes"] = attributes
        self.logger.error(message, **kwargs)
