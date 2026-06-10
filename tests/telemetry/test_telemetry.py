import pytest

from unittest.mock import Mock, patch

from pylog.telemetry.telemetry import TelemetryManager, get_tracer, custom_span


def test_telemetry_manager_initialization():
    tm = TelemetryManager()

    assert tm._started is False
    assert tm._meter is None
    assert tm._service_name is None


def test_get_meter_before_init_raises_error():
    tm = TelemetryManager()

    with pytest.raises(RuntimeError):
        tm.get_meter()


@patch("pylog.telemetry.telemetry.get_project_name")
def test_init_telemetry_sets_started(mock_project):

    mock_project.return_value = "test-services"
    tm = TelemetryManager()

    tm.init_telemetry()

    assert tm._started is True


@patch("pylog.telemetry.telemetry.get_project_name")
def test_init_telemetry_service_name_saved(mock_project):

    mock_project.return_value = "test-services"

    tm = TelemetryManager()

    tm.init_telemetry()

    assert tm._service_name == "test-services"


@patch("pylog.telemetry.telemetry.get_project_name")
def test_init_telemetry_only_runs_once(mock_project):

    mock_project.return_value = "service"

    tm = TelemetryManager()

    tm.init_telemetry()

    first_state = tm._started

    tm.init_telemetry()

    assert first_state is True
    assert tm._started is True


@patch("pylog.telemetry.telemetry.OTLPSpanExporter")
@patch("pylog.telemetry.telemetry.get_project_name")
def test_trace_exporter_created(mock_project, mock_exporter):

    mock_project.return_value = "service"

    tm = TelemetryManager()

    tm.init_telemetry(trace_exporter_endpoint="http://localhost:4318/v1/traces")

    mock_exporter.assert_called_once()


@patch("pylog.telemetry.telemetry.OTLPSpanExporter")
@patch("pylog.telemetry.telemetry.get_project_name")
def test_metrics_exporter_created(mock_project, mock_exporter):

    mock_exporter.return_value = "service"

    tm = TelemetryManager()

    tm.init_telemetry(metric_exporter_endpoint="http://localhost:4318/v1/metrics")

    mock_exporter.assert_called_once()


@patch("pylog.telemetry.telemetry.OTLPSpanExporter")
@patch("pylog.telemetry.telemetry.get_project_name")
def test_logs_exporter_created(mock_project, mock_exporter):

    mock_exporter.return_value = "service"

    tm = TelemetryManager()

    tm.init_telemetry(log_exporter_endpoint="http://localhost:4318/v1/logs")

    mock_exporter.assert_called_once()


@patch("pylog.telemetry.telemetry.trace.set_tracer_provider")
@patch("pylog.telemetry.telemetry.get_project_name")
def test_tracer_provider_set(mock_project, mock_set_provider):

    mock_project.return_value = "service"

    tm = TelemetryManager()

    tm.init_telemetry()

    mock_set_provider.assert_called_once()


@patch("pylog.telemetry.telemetry.trace.get_tracer")
def test_get_tracer(mock_get_tracer):

    get_tracer()

    mock_get_tracer.assert_called_once_with("simple-otel-logger")


@patch("pylog.telemetry.telemetry.trace.get_tracer")
def test_custom_span_creates_span(mock_get_tracer):

    fake_span = Mock()

    mock_cm = Mock()
    mock_cm.__enter__ = Mock(return_value=fake_span)
    mock_cm.__exit__ = Mock(return_value=None)

    mock_tracer = Mock()
    mock_tracer.start_as_current_span.return_value = mock_cm

    mock_get_tracer.return_value = mock_tracer

    with custom_span("db-query"):
        pass

    mock_tracer.start_as_current_span.assert_called_once_with("db-query")


@patch("pylog.telemetry.telemetry.trace.get_tracer")
def test_custom_span_sets_attributes(mock_get_tracer):
    fake_span = Mock()

    mock_cm = Mock()
    mock_cm.__enter__ = Mock(return_value=fake_span)
    mock_cm.__exit__ = Mock(return_value=None)

    mock_tracer = Mock()
    mock_tracer.start_as_current_span.return_value = mock_cm

    mock_get_tracer.return_value = mock_tracer

    with custom_span(
        "db-query",
        {
            "db.system": "postgresql",
            "table": "users",
        },
    ):
        pass

    assert fake_span.set_attribute.call_count == 2
