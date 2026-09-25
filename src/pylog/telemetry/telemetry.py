from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import requests

resource = Resource.create(attributes={SERVICE_NAME: "Unknown-service"})

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


def get_vllm_metrics(port: int):
    address = f"http://vllm:{port}/metrics"
    try:
        response = requests.get(address)
        if response.status_code == 200:
            return response.text
    except requests.RequestException as exc:
        print(f"Failed to fetch vLLM metrics: {exc}")
