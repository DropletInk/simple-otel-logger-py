import os
from pylog.telemetry import (
    add_metric_exporter,
    add_traces_span_exporter,
    enable_system_metrics,
)

OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "unknown-service")

OTEL_EXPORTER_TRACE_ENDPOINT = os.getenv("OTEL_EXPORTER_TRACE_ENDPOINT", None)

OTEL_EXPORTER_METRIC_ENDPOINT = os.getenv(
    "OTEL_EXPORTER_METRIC_ENDPOINT", None
)

OTEL_EXPORTER_LOGS_ENDPOINT = os.getenv("OTEL_EXPORTER_LOGS_ENDPOINT", None)


OTEL_ENABLE_SYSTEM_METRICS = os.getenv(
    "OTEL_ENABLE_SYSTEM_METRICS", "True"
).lower() in ("1", "true", "yes")


def _get_metrics_logger():
    from pylog.logger import ConsoleLogger

    return ConsoleLogger(service_name=OTEL_SERVICE_NAME)

def configure_telemetry() -> None:
    """Configure OpenTelemetry exporters and system metrics."""
    add_metric_exporter(
        OTEL_EXPORTER_METRIC_ENDPOINT,  # None is fine — add_metric_exporter already branches on this
        logger=_get_metrics_logger(),
    )

    if OTEL_EXPORTER_TRACE_ENDPOINT:
        add_traces_span_exporter(OTEL_EXPORTER_TRACE_ENDPOINT)

    if OTEL_ENABLE_SYSTEM_METRICS:
        enable_system_metrics()


def get_environment():
    return os.getenv("ENVIRONMENT", "development")


def get_console_enabled() -> bool:
    return os.getenv("LOG_ON_CONSOLE", "True")

configure_telemetry()