from opentelemetry import _logs, metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from contextlib import contextmanager
from .project import get_project_name

# logs
from opentelemetry.sdk._logs import LoggerProvider

# metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

# traces
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


class TelemetryManager:
    def __init__(self):
        self._started = False
        self._meter = None
        self._service_name = None

    def init_telemetry(
        self,
        service_name: str | None = None,
        trace_exporter_endpoint: str | None = None,
        metric_exporter_endpoint: str | None = None,
        log_exporter_endpoint: str | None = None,
        environment: str = "development",
    ):
        service_name = get_project_name()
        self._service_name = service_name
        if self._started:
            return

        resource = Resource.create(
            {
                "service.name": service_name,
                "deployment.environment": environment,
            }
        )

        # For Traces

        tracer_provider = TracerProvider(
            resource=resource,
        )

        if trace_exporter_endpoint:
            trace_exporter = OTLPSpanExporter(
                endpoint=trace_exporter_endpoint,
            )

            tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

        trace.set_tracer_provider(tracer_provider)

        # For metrics

        if metric_exporter_endpoint:
            metric_exporter = OTLPMetricExporter(
                endpoint=metric_exporter_endpoint,
            )

            metric_reader = PeriodicExportingMetricReader(
                exporter=metric_exporter,
                export_interval_millis=5000,
            )

            meter_provider = MeterProvider(
                resource=resource,
                metric_readers=[metric_reader],
            )

            metrics.set_meter_provider(meter_provider)

            self._meter = metrics.get_meter(service_name, version="1.0.0")

        # For   logs
        logger_provider = LoggerProvider(
            resource=resource,
        )

        _logs.set_logger_provider(logger_provider)

        self._started = True

    def get_meter(self):
        if self._meter is None:
            raise RuntimeError("Telemetry has not been initialized. Please call init_telemetry first.")

        return self._meter


# tracer
def get_tracer(name: str = "simple-otel-logger"):
    return trace.get_tracer(name)


@contextmanager
def custom_span(
    name: str,
    attributes: dict | None = None,
):
    tracer = trace.get_tracer("simple-otel-logger")

    with tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        yield span
