import os
from pylog.telemetry import add_metric_exporter, add_traces_span_exporter


SIMPLE_OTEL_LOGGER_ENV = os.getenv("SIMPLE_OTEL_LOGGER_ENV", "Production")

OTEL_EXPORTER_TRACE_ENDPOINT = os.gotenv("OTEL_EXPORTER_TRACE_ENDPOINT", None)

OTEL_EXPORTER_METRIC_ENDPOINT = os.gotenv("OTEL_EXPORTER_METRIC_ENDPOINT", None)

OTEL_EXPORTER_LOGS_ENDPOINT = os.gotenv("OTEL_EXPORTER_LOGS_ENDPOINT", None)


add_metric_exporter(OTEL_EXPORTER_METRIC_ENDPOINT)
add_traces_span_exporter(OTEL_EXPORTER_TRACE_ENDPOINT)
