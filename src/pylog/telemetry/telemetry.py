# pylog/telemetry.py
import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.system_metrics import (
    SystemMetricsInstrumentor,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    MetricExporter,
    MetricExportResult,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "unknown-service")
OTEL_METRIC_EXPORT_INTERVAL_MS = int(
    os.getenv("OTEL_METRIC_EXPORT_INTERVAL_MS", "5000")
)

resource = Resource.create(attributes={SERVICE_NAME: OTEL_SERVICE_NAME})

tracerProvider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracerProvider)

provider = trace.get_tracer_provider()

_meter_provider: MeterProvider | None = None
_system_metrics_instrumented = False


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


class SimpleConsoleMetricExporter(MetricExporter):
    DEFAULT_WATCHED = {
        "system.cpu.utilization",
        "system.memory.usage",
        "process.cpu.utilization",
        "process.runtime.cpython.memory",
    }

    def __init__(self, watched: set[str] | None = None, logger_factory=None):
        super().__init__()
        self.watched = watched
        self._last_printed: dict[tuple, str] = {}
        self._logger_factory = logger_factory
        self._logger = None

    def _get_logger(self):
        """Builds the logger on first use, not at construction time."""
        if self._logger is None and self._logger_factory is not None:
            self._logger = self._logger_factory()
        return self._logger

    def export(self, metrics_data, **kwargs) -> MetricExportResult:
        for resource_metrics in metrics_data.resource_metrics:
            service_name = resource_metrics.resource.attributes.get(
                "service.name", "unknown"
            )
            for scope_metrics in resource_metrics.scope_metrics:
                for metric in scope_metrics.metrics:
                    if (
                        self.watched is not None
                        and metric.name not in self.watched
                    ):
                        continue
                    self._print_metric(service_name, metric)
        return MetricExportResult.SUCCESS

    def _emit(
        self,
        key: tuple,
        message: str,
        attributes: dict | None = None,
        cpu_metrics: dict | None = None,
        gpu_metrics: dict | None = None,
    ) -> None:
        if self._last_printed.get(key) == message:
            return
        self._last_printed[key] = message

        logger = self._get_logger()
        if logger is not None:
            logger.info(
                message,
                eventName="MetricExport",
                attributes=attributes or {},
                cpu_metrics=cpu_metrics or {},
                gpu_metrics=gpu_metrics or {},
            )
        else:
            print(message)

    # Printing the Metrics in the human Readable format
    def _print_metric(self, service_name: str, metric) -> None:
        points = metric.data.data_points
        name = metric.name

        if name == "system.cpu.utilization":
            busy = [
                p.value
                for p in points
                if p.attributes.get("state") in ("user", "system")
            ]
            avg_busy_pct = (sum(busy) / len(busy)) * 100 if busy else 0
            per_core = {
                f"cpu_{p.attributes.get('cpu')}_{p.attributes.get('state')}": round(
                    p.value * 100, 2
                )
                for p in points
            }
            self._emit(
                (service_name, name),
                f"CPU usage: {avg_busy_pct:.1f}%",
                cpu_metrics={
                    "system_cpu_utilization_pct": round(avg_busy_pct, 1),
                    **per_core,
                },
            )

        elif name == "system.memory.usage":
            values = {p.attributes.get("state"): p.value for p in points}
            used_gb = values.get("used", 0) / (1024**3)
            free_gb = values.get("free", 0) / (1024**3)
            self._emit(
                (service_name, name),
                f"Memory: {used_gb:.2f} GB used / {free_gb:.2f} GB free",
                cpu_metrics={
                    "metric": name,
                    "used_gb": round(used_gb, 2),
                    "free_gb": round(free_gb, 2),
                },
            )

        elif name == "process.cpu.utilization":
            for p in points:
                self._emit(
                    (service_name, name),
                    f"Process CPU: {p.value * 100:.2f}%",
                    cpu_metrics={
                        "process_cpu_utilization_pct": round(p.value * 100, 2)
                    },
                )

        elif name == "process.runtime.cpython.memory":
            values = {p.attributes.get("type"): p.value for p in points}
            rss_mb = values.get("rss", 0) / (1024**2)
            self._emit(
                (service_name, name),
                f"Process memory (RSS): {rss_mb:.1f} MB",
                cpu_metrics={"metric": name, "rss_mb": round(rss_mb, 1)},
            )

        elif points and hasattr(points[0], "bucket_counts"):
            for p in points:
                attrs = dict(p.attributes)
                job_id = attrs.pop("job_id", None)
                label = f"{name}" + (f" [job={job_id}]" if job_id else "")
                avg = p.sum / p.count if p.count else 0
                key = (service_name, name, job_id)
                self._emit(
                    key,
                    f"{label}: count={p.count}, avg={avg:.3f}, min={p.min:.3f}, max={p.max:.3f}",
                    cpu_metrics={
                        "metric": name,
                        "count": p.count,
                        "avg": round(avg, 3),
                        "min": round(p.min, 3),
                        "max": round(p.max, 3),
                        "job_id": job_id,
                    },
                )

        elif hasattr(metric.data, "aggregation_temporality"):
            for p in points:
                attrs = dict(p.attributes)
                job_id = attrs.pop("job_id", None)
                label = f"{name}" + (f" [job={job_id}]" if job_id else "")
                key = (service_name, name, job_id)
                self._emit(
                    key,
                    f"{label}: {p.value}",
                    cpu_metrics={
                        "metric": name,
                        "value": p.value,
                        "job_id": job_id,
                    },
                )

    # Forcing that nothing left in the exporter
    def force_flush(self, timeout_millis: float = 10_000) -> bool:
        return True

    # It ensures that the last minute data is out of the exporter
    def shutdown(self, timeout_millis: float = 30_000, **kwargs) -> None:
        pass


# Metrics exporter , periodic exporter  if endpoint is provided then export there else print on console
def add_metric_exporter(
    OTLP_Metric_exporter_endpoint=None,
    watched: set[str] | None = None,
    logger_factory=None,
) -> MeterProvider:
    global _meter_provider

    if OTLP_Metric_exporter_endpoint:
        reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=OTLP_Metric_exporter_endpoint),
            export_interval_millis=OTEL_METRIC_EXPORT_INTERVAL_MS,
        )
    else:
        reader = PeriodicExportingMetricReader(
            SimpleConsoleMetricExporter(
                watched=watched, logger_factory=logger_factory
            ),
            export_interval_millis=OTEL_METRIC_EXPORT_INTERVAL_MS,
        )

    _meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(_meter_provider)
    return _meter_provider


# Helper functions
def get_meter(name: str | None = None) -> metrics.Meter:
    """Public entrypoint for app code — returns a Meter bound to the
    shared MeterProvider, using OTEL_SERVICE_NAME as the default scope name."""
    return metrics.get_meter(name or OTEL_SERVICE_NAME)


def get_meter_provider() -> MeterProvider | None:
    return _meter_provider


def force_flush_metrics(timeout_millis: int = 5000) -> None:
    """Immediately export current metric values instead of waiting for the
    periodic interval — useful for per-item progress visibility."""
    if _meter_provider is not None:
        _meter_provider.force_flush(timeout_millis)


def enable_system_metrics(config: dict | None = None) -> None:
    """Registers OS/process-level metrics (CPU, memory, GC) on the shared
    provider. Safe to call more than once — only instruments on the first call."""
    global _system_metrics_instrumented
    if _system_metrics_instrumented:
        return

    default_config = {
        "process.runtime.cpython.memory": ["rss", "vms"],
        "process.cpu.utilization": None,
        "process.runtime.cpython.gc_count": None,
        "system.cpu.utilization": ["idle", "user", "system"],
        "system.memory.usage": ["used", "free", "cached"],
    }
    SystemMetricsInstrumentor(config=config or default_config).instrument()
    _system_metrics_instrumented = True
