import logging
import sys
import structlog
from opentelemetry import trace


def add_log_level(logger, method_name, event_dict):
    event_dict["level"] = method_name
    return event_dict


def rename_event_key(logger, method_name, event_dict):
    if "event" in event_dict:
        event_dict["message"] = event_dict.pop("event")
    return event_dict


def add_otel_context(logger, method_name, event_dict):
    span = trace.get_current_span()
    ctx = span.get_span_context()

    if ctx and ctx.is_valid:
        event_dict["traceId"] = format(ctx.trace_id, "032x")
        event_dict["spanId"] = format(ctx.span_id, "016x")

    return event_dict


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.StreamHandler(sys.stderr),
        ],
    )

    structlog.configure(
        processors=[
            add_log_level,
            structlog.processors.TimeStamper(
                fmt="iso", utc=True, key="timestamp"
            ),
            add_otel_context,
            rename_event_key,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
