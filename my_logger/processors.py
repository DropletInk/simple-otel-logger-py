import socket

from opentelemetry.trace import get_current_span


def add_app_metadata(logger, method_name, event_dict) -> dict:

    event_dict["hostname"] = socket.gethostname()

    return event_dict


def add_trace_context(logger, method_name, event_dict) -> dict:

    span = get_current_span()

    span_context = span.get_span_context()

    if span_context.is_valid:
        event_dict["trace_id"] = format(span_context.trace_id, "032x")

        event_dict["span_id"] = format(span_context.span_id, "016x")

    return event_dict
