from pylog.types.types import LogRecord, LoggerOptions, Severity

def test_severity_values():
    assert Severity.DEBUG == 5
    assert Severity.INFO == 9
    assert Severity.WARN == 13
    assert Severity.ERROR == 17


def test_log_record_creation():
    record: LogRecord = {
        "level": "INFO",
        "message": "User logged in",
        "attributes": {
            "user_id": 1,
        },
    }

    assert record["level"] == "INFO"
    assert record["message"] == "User logged in"
    assert record["attributes"]["user_id"] == 1


def test_logger_options():
    record: LoggerOptions = {"service_name": "app-service"}

    assert record["service_name"] == "app-service"
