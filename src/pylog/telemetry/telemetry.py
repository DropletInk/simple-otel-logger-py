from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry import metrics, trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from pylog.utils import get_project_name

resource = Resource.create(attributes={SERVICE_NAME: get_project_name()})

tracerProvider = TracerProvider(resource=resource)

trace.set_tracer_provider(tracerProvider)


provider = trace.get_tracer_provider()


def get_tracer() -> object:
    if not isinstance(provider, TracerProvider):
        trace.set_tracer_provider(TracerProvider())
    return trace.get_tracer(__name__)


def add_traces_span_exporter(OTLP_Span_exporter_endpoint=None) -> None:
    if OTLP_Span_exporter_endpoint:
        processor = BatchSpanProcessor(
            OTLPSpanExporter(endpoint=OTLP_Span_exporter_endpoint)
        )
        provider.add_span_processor(  # ty:ignore[unresolved-attribute]
            processor
        )
        trace.set_tracer_provider(provider)


def add_metric_exporter(OTLP_Metric_exporter_endpoint=None) -> None:
    if OTLP_Metric_exporter_endpoint:
        reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=OTLP_Metric_exporter_endpoint)
        )
        meterProvider = MeterProvider(
            resource=resource, metric_readers=[reader]
        )
        metrics.set_meter_provider(meterProvider)
