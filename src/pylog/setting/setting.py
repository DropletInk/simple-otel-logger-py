import os

from pylog.telemetry import add_metric_exporter, add_traces_span_exporter

OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "unknown-service")

OTEL_EXPORTER_TRACE_ENDPOINT = os.getenv("OTEL_EXPORTER_TRACE_ENDPOINT", None)

OTEL_EXPORTER_METRIC_ENDPOINT = os.getenv(
    "OTEL_EXPORTER_METRIC_ENDPOINT", None
)

OTEL_EXPORTER_LOGS_ENDPOINT = os.getenv("OTEL_EXPORTER_LOGS_ENDPOINT", None)

add_metric_exporter(OTEL_EXPORTER_METRIC_ENDPOINT)
add_traces_span_exporter(OTEL_EXPORTER_TRACE_ENDPOINT)


def get_environment():
    return os.getenv("ENVIRONMENT", "production")


def get_console_enabled() -> bool:
    return os.getenv("LOG_ON_CONSOLE", "True")
