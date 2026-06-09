import os

from dotenv import load_dotenv
from telemetry import init_telemetry

PY_ENV = os.getenv("PY_ENV", "development")

OTEL_EXPORTER_TRACE_ENDPOINT = os.getenv("OTEL_EXPORTER_TRACE_ENDPOINT", "None")

OTEL_EXPORTER_LOG_ENDPOINT = os.getenv("OTEL_EXPORTER_LOG_ENDPOINT", "None")

OTEL_EXPORTER_METRICS_ENDPOINT = os.getenv("OTEL_EXPORTER_METRICS_ENDPOINT", "None")


def initialise_service():
    load_dotenv()
    init_telemetry(
        OTEL_EXPORTER_TRACE_ENDPOINT,
        OTEL_EXPORTER_METRICS_ENDPOINT,
        OTEL_EXPORTER_LOG_ENDPOINT,
        PY_ENV,
    )
