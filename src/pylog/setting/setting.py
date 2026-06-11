import os

from dotenv import load_dotenv
from pylog.telemetry import TelemetryManager

LOGGER_ENV = os.getenv("LOGGER_ENV", "development")

OTEL_EXPORTER_TRACE_ENDPOINT = os.getenv("OTEL_EXPORTER_TRACE_ENDPOINT", "None")

OTEL_EXPORTER_LOG_ENDPOINT = os.getenv("OTEL_EXPORTER_LOG_ENDPOINT", "None")

OTEL_EXPORTER_METRICS_ENDPOINT = os.getenv("OTEL_EXPORTER_METRICS_ENDPOINT", "None")


def initialise_service():
    load_dotenv()
    TelemetryManager().init_telemetry(
        OTEL_EXPORTER_TRACE_ENDPOINT,
        OTEL_EXPORTER_METRICS_ENDPOINT,
        OTEL_EXPORTER_LOG_ENDPOINT,
        LOGGER_ENV,
    )
