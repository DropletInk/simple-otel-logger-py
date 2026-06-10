from unittest.mock import Mock, patch

from pylog import counter, histogram, create_counter, _metrics


@patch("pylog.metrics.metrics.TelemetryManager.get_meter")
def test_counter_creats_metrics(mock_get_meter):
    _metrics.clear()

    fake_counter = Mock()

    fake_meter = Mock()
    fake_meter.create_counter.return_value = fake_counter

    mock_get_meter.return_value = fake_meter

    result = counter("requests_total")

    assert result == fake_counter
    fake_meter.create_counter.assert_called_once()


@patch("pylog.metrics.metrics.TelemetryManager.get_meter")
def test_counter_reuses_existing_metric(mock_get_meter):
    _metrics.clear()

    fake_counter = Mock()

    fake_meter = Mock()
    fake_meter.create_counter.return_value = fake_counter

    mock_get_meter.return_value = fake_meter

    counter("requests_total")
    counter("requests_total")

    fake_meter.create_counter.assert_called_once()


@patch("pylog.metrics.metrics.TelemetryManager.get_meter")
def test_histogram_creates_metric(mock_get_meter):
    _metrics.clear()

    fake_histogram = Mock()

    fake_meter = Mock()
    fake_meter.create_histogram.return_value = fake_histogram

    mock_get_meter.return_value = fake_meter

    result = histogram("request_duration")

    assert result == fake_histogram
    fake_meter.create_histogram.assert_called_once()


@patch("pylog.metrics.metrics.TelemetryManager.get_meter")
def test_histogram_reuses_existing_metric(mock_get_meter):
    _metrics.clear()

    fake_histogram = Mock()

    fake_meter = Mock()
    fake_meter.create_histogram.return_value = fake_histogram

    mock_get_meter.return_value = fake_meter

    histogram("request_duration")
    histogram("request_duration")

    fake_meter.create_histogram.assert_called_once()


@patch("pylog.metrics.metrics.TelemetryManager.get_meter")
def test_create_counter_always_creates_new_counter(mock_get_meter):
    fake_meter = Mock()

    mock_get_meter.return_value = fake_meter

    create_counter("requests")
    create_counter("requests")

    assert fake_meter.create_counter.call_count == 2


@patch("pylog.metrics.metrics.TelemetryManager.get_meter")
def test_create_counter_custom_values(mock_get_meter):
    fake_meter = Mock()

    mock_get_meter.return_value = fake_meter

    create_counter(
        "requests",
        description="Total Requests",
        unit="req",
    )

    fake_meter.create_counter.assert_called_once_with(
        name="requests",
        description="Total Requests",
        unit="req",
    )
