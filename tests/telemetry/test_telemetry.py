from unittest.mock import MagicMock, patch

from pylog.telemetry import get_tracer


@patch("pylog.telemetry.telemetry.trace.get_tracer")
def test_get_tracer(mock_get_tracer):
    tracer = MagicMock()
    mock_get_tracer.return_value = tracer

    result = get_tracer()

    assert result == tracer
