from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pylog.telemetry.telemetry as telemetry


def make_point(**kwargs):
    return SimpleNamespace(**kwargs)


def make_metric(name, points, **extra_data):
    data = SimpleNamespace(data_points=points, **extra_data)
    return SimpleNamespace(name=name, data=data)


def test_cpu_utilization_prints_percentage(capsys):
    exporter = telemetry.SimpleConsoleMetricExporter()
    points = [
        make_point(value=0.3, attributes={"state": "user", "cpu": "0"}),
        make_point(value=0.2, attributes={"state": "system", "cpu": "0"}),
    ]
    exporter._print_metric(
        "svc", make_metric("system.cpu.utilization", points)
    )
    assert "CPU usage: 25.0%" in capsys.readouterr().out


def test_memory_usage_prints_gb(capsys):
    exporter = telemetry.SimpleConsoleMetricExporter()
    gb = 1024**3
    points = [
        make_point(value=2 * gb, attributes={"state": "used"}),
        make_point(value=6 * gb, attributes={"state": "free"}),
    ]
    exporter._print_metric("svc", make_metric("system.memory.usage", points))
    out = capsys.readouterr().out
    assert "2.00 GB used" in out
    assert "6.00 GB free" in out


def test_process_cpu_prints_percentage(capsys):
    exporter = telemetry.SimpleConsoleMetricExporter()
    points = [make_point(value=0.157, attributes={})]
    exporter._print_metric(
        "svc", make_metric("process.cpu.utilization", points)
    )
    assert "Process CPU: 15.70%" in capsys.readouterr().out


def test_process_memory_prints_rss_mb(capsys):
    exporter = telemetry.SimpleConsoleMetricExporter()
    mb = 1024**2
    points = [make_point(value=128 * mb, attributes={"type": "rss"})]
    exporter._print_metric(
        "svc", make_metric("process.runtime.cpython.memory", points)
    )
    assert "Process memory (RSS): 128.0 MB" in capsys.readouterr().out


def test_histogram_metric_prints_stats(capsys):
    exporter = telemetry.SimpleConsoleMetricExporter()
    point = make_point(
        attributes={"job_id": "job-1"},
        count=2,
        sum=20.0,
        min=5.0,
        max=15.0,
        bucket_counts=[1, 1],
    )
    exporter._print_metric("svc", make_metric("job.duration", [point]))
    out = capsys.readouterr().out
    assert "job.duration [job=job-1]" in out
    assert "count=2" in out
    assert "avg=10.000" in out


def test_sum_metric_prints_value(capsys):
    exporter = telemetry.SimpleConsoleMetricExporter()
    point = make_point(attributes={"job_id": "job-7"}, value=99)
    metric = make_metric("custom.counter", [point], aggregation_temporality=2)
    exporter._print_metric("svc", metric)
    assert "custom.counter [job=job-7]: 99" in capsys.readouterr().out


def test_unknown_metric_shape_prints_nothing(capsys):
    exporter = telemetry.SimpleConsoleMetricExporter()
    point = make_point(attributes={}, value=1)
    exporter._print_metric("svc", make_metric("weird.metric", [point]))
    assert capsys.readouterr().out == ""


def test_emit_prints_once_for_repeated_message(capsys):
    exporter = telemetry.SimpleConsoleMetricExporter()
    key = ("svc", "m")
    exporter._emit(key, "same message")
    exporter._emit(key, "same message")
    assert capsys.readouterr().out.count("same message") == 1


def test_emit_prints_again_when_message_changes(capsys):
    exporter = telemetry.SimpleConsoleMetricExporter()
    key = ("svc", "m")
    exporter._emit(key, "message A")
    exporter._emit(key, "message B")
    out = capsys.readouterr().out
    assert "message A" in out
    assert "message B" in out


def test_emit_uses_logger_when_provided():
    mock_logger = MagicMock()
    exporter = telemetry.SimpleConsoleMetricExporter(
        logger_factory=lambda: mock_logger
    )
    exporter._emit(("svc", "m"), "msg")
    mock_logger.info.assert_called_once()


def test_export_skips_metrics_not_watched():
    exporter = telemetry.SimpleConsoleMetricExporter(watched={"wanted.metric"})
    metric = make_metric("other.metric", [])
    data = SimpleNamespace(
        resource_metrics=[
            SimpleNamespace(
                resource=SimpleNamespace(attributes={"service.name": "svc"}),
                scope_metrics=[SimpleNamespace(metrics=[metric])],
            )
        ]
    )
    with patch.object(exporter, "_print_metric") as mock_print:
        exporter.export(data)
        mock_print.assert_not_called()


def test_export_returns_success():
    exporter = telemetry.SimpleConsoleMetricExporter()
    result = exporter.export(SimpleNamespace(resource_metrics=[]))
    from opentelemetry.sdk.metrics.export import MetricExportResult

    assert result == MetricExportResult.SUCCESS


def test_force_flush_returns_true():
    assert telemetry.SimpleConsoleMetricExporter().force_flush() is True


def test_shutdown_does_not_raise():
    telemetry.SimpleConsoleMetricExporter().shutdown()


def test_get_meter_uses_given_name():
    with patch.object(
        telemetry.metrics, "get_meter", return_value="meter"
    ) as mock_get:
        result = telemetry.get_meter("custom.scope")
        mock_get.assert_called_once_with("custom.scope")
        assert result == "meter"


def test_get_meter_defaults_to_service_name():
    with patch.object(
        telemetry.metrics, "get_meter", return_value="meter"
    ) as mock_get:
        telemetry.get_meter()
        mock_get.assert_called_once_with(telemetry.OTEL_SERVICE_NAME)


def test_force_flush_metrics_noop_when_no_provider():
    telemetry._meter_provider = None
    telemetry.force_flush_metrics()


def test_force_flush_metrics_calls_provider():
    mock_provider = MagicMock()
    telemetry._meter_provider = mock_provider
    telemetry.force_flush_metrics(timeout_millis=1234)
    mock_provider.force_flush.assert_called_once_with(1234)


def test_enable_system_metrics_instruments_once():
    telemetry._system_metrics_instrumented = False
    with patch(
        "pylog.telemetry.telemetry.SystemMetricsInstrumentor"
    ) as MockInstrumentor:
        telemetry.enable_system_metrics()
        telemetry.enable_system_metrics()
        MockInstrumentor.assert_called_once()
