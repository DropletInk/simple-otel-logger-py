import pytest
from pylog.logger import rename_level, otel_tags, log_organiser, ConsoleLogger
import json 

def test_rename_level():
    event = {"level": "info"}

    result = rename_level(None, None, event)

    assert result["severityText"] == "INFO"
    assert result["severityNumber"] == 9


def test_otel_tags():
    event = {}

    result = otel_tags(None, None, event)

    assert result["instrumentationScope"]["name"] == "simple-otel-logger"
    assert result["instrumentationScope"]["version"] == "1.0.0"


def test_log_organiser():
    event = {
        "resources": {"service_name": "test"},
        "instrumentationScope": {"name": "test"},
        "event": "hello",
    }

    result = log_organiser(None, None, event)
    assert result["resources"]["service_name"] == "test"

#testing ConsoleLogger 
def test_consolelogger(capsys):
    log = ConsoleLogger("test")
    log.info("testing console logger",attributes={"id":123})

    captured = capsys.readouterr()

    log_output = json.loads(captured.out.strip())

    assert log_output["event"] == "testing console logger" 
    assert log_output['severityText'] =='INFO'
    assert log_output['attributes'] == {'id':123}
