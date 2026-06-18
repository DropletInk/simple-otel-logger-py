from unittest.mock import MagicMock, patch

from pylog.telemetry import get_tracer,add_traces_span_exporter,add_metric_exporter
from opentelemetry.sdk.trace  import TracerProvider

@patch("pylog.telemetry.telemetry.trace.set_tracer_provider")
@patch("pylog.telemetry.telemetry.trace.get_tracer")
def test_get_tracer_sets_tracer_provider_is_valid(mock_get_tracer,mocke_set_provider):
    tracer = MagicMock()
    mock_get_tracer.return_value = tracer

    with patch(
        "pylog.telemetry.telemetry.provider",
        object(),
    ):
        result = get_tracer()

    mocke_set_provider.assert_called_once()
    assert result == tracer


@patch("pylog.telemetry.telemetry.trace.set_tracer_provider")
def test_get_tracer_sets_tracer_provider_is_not_valid( mocke_set_provider ):

    with patch(
        "pylog.telemetry.telemetry.provider",
        TracerProvider()
    ):
        get_tracer()

    mocke_set_provider.assert_not_called()


#checking for trace span exporter emdpoint provided or not

@patch("pylog.telemetry.telemetry.OTLPSpanExporter")
def test_trace_exporter_created_with_endpoint(mock_exporter):

    with patch(
        "pylog.telemetry.telemetry.provider",
        MagicMock()
    ):

        add_traces_span_exporter("http://localhost:4341/v1/traces")
    
    mock_exporter.assert_called_once_with(endpoint = "http://localhost:4341/v1/traces")



# verify if no endpoint is provided
@patch("pylog.telemetry.telemetry.OTLPSpanExporter")
def test_trace_exporter_created_with_no_endpoint(mock_exporter):

    add_traces_span_exporter(None)

    mock_exporter.assert_not_called()

# checking for metric exporter endpoint provided or not

@patch("pylog.telemetry.telemetry.OTLPMetricExporter")
def test_metric_exporter_created_with_endpoint(mock_exporter):

    with patch("pylog.telemetry.telemetry.provider", MagicMock()):
        add_metric_exporter("http://localhost:4341/v1/metrics")

    mock_exporter.assert_called_once_with(
        endpoint="http://localhost:4341/v1/metrics"
    )


# verify if no endpoint is provided
@patch("pylog.telemetry.telemetry.OTLPMetricExporter")
def test_metric_exporter_created_with_no_endpoint(mock_exporter):

    add_metric_exporter(None)

    mock_exporter.assert_not_called()