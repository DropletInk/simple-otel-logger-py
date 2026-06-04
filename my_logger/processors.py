import socket

from opentelemetry.trace import get_current_span

SENSITIVE_KEYS = {"password", "token", "secret", "api_key"}


def mask_sensitive_data(logger, method_name, event_dict):

    for key in SENSITIVE_KEYS:
        if key in event_dict:
            event_dict[key] = "***MASKED***"

    return event_dict


def add_app_metadata(logger, method_name, event_dict):

    event_dict["hostname"] = socket.gethostname()

    return event_dict


def add_trace_context(logger, method_name, event_dict):

    span = get_current_span()

    span_context = span.get_span_context()

    if span_context.is_valid:
        event_dict["trace_id"] = format(span_context.trace_id, "032x")

        event_dict["span_id"] = format(span_context.span_id, "016x")

        event_dict["trace_flags"] = int(span_context.trace_flags)

    return event_dict


def rename_level(logger, method_name, event_dict):
    mapping = {
        "DEBUG": 5,
        "INFO": 9,
        "WARNING": 13,
        "ERROR": 17,
        "CRITICAL": 21,
    }
    if "level" in event_dict:
        event_dict["severityText"] = event_dict.pop("level").upper()
        event_dict["severityNumber"] = mapping.get(event_dict["severityText"], 0)
    return event_dict
