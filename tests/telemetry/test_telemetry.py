from pylog.telemetry import (
    get_tracer,
    add_traces_span_exporter,
    add_metric_exporter,
)
import pytest
from opentelemetry import metrics


def test_get_tracer_returns_tracer():
    tracer = get_tracer()
    print(tracer)
    assert tracer is not None


def test_running_of_span_exporter():
    try:
        add_traces_span_exporter("http://localhost:4318/v1/traces")
    except Exception as e:
        pytest.fail(f"Something went wrong {e}")


def test_add_metric_exporter():
    try:
        add_metric_exporter("http://localhost:4318/v1/metrics")
        provider = metrics.get_meter_provider()
        assert provider is not None
    except Exception as e:
        pytest.fail(f"Something went wrong {e}")


def test_add_traces_span_exporter():
    try:
        add_traces_span_exporter("http://localhost:4318/v1/traces")

        tracer = get_tracer()
        with tracer.start_as_current_span("test-span") as span:  # ty:ignore[unresolved-attribute]
            assert span is not None
    except Exception as e:
        pytest.fail(f"Something went wrong {e}")


def test_add_metric_exporter_does_not_raise():
    try:
        add_metric_exporter("http://localhost:4318/v1/metrics")
        meter = metrics.get_meter(__name__)

        counter = meter.create_counter("test-counter")
        counter.add(2)
        assert counter is not None
    except Exception as e:
        pytest.fail(f"Something went wrong {e}")
