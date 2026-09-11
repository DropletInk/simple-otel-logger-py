import json
import re

from pylog.logger import ConsoleLogger, log_organiser, otel_tags, rename_level


def test_rename_level():
    event = {"level": "info"}

    result = rename_level(None, None, event)

    assert result["severityText"] == "INFO"
    assert result["severityNumber"] == 9


def test_otel_tags():
    event = {}

    result = otel_tags(None, None, event)

    assert result["instrumentationScope"]["name"] == "pylog"
    assert result["instrumentationScope"]["version"] == "1.0.0"


def test_log_organiser():
    event = {
        "resources": {"service_name": "test"},
        "instrumentationScope": {"name": "test"},
        "event": "hello",
    }

    result = log_organiser(None, None, event)
    assert result["resources"]["service_name"] == "test"


# testing ConsoleLogger
def test_consolelogger(capsys, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")

    log = ConsoleLogger("test")

    log.info("testing console logger", attributes={"id": 123})

    captured = capsys.readouterr()

    clean_output = re.sub(r"\x1b\[[0-9;]*m", "", captured.out)

    log_output = json.loads(clean_output.strip())

    assert log_output["body"] == "testing console logger"
    assert log_output["attributes"] == {"id": 123}
