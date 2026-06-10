import pytest
from unittest.mock import Mock, patch
from pylog import Logger, get_logger, get_otel_context, configure_structlog, traced


# Testing Logger Initialization
def test_logger_initialization():
    logger = Logger(
        service_name="test-service",
        base={"env": "test"},
        custom_level="DEBUG",
    )

    assert logger.service_name == "test-service"
    assert logger.base == {"env": "test"}
    assert logger.custom_level == "DEBUG"


# Testing Default initialization
def test_logger_default_initialization():
    logger = Logger()

    assert logger.service_name == "app-service"
    assert logger.base == {}
    assert logger.custom_level is None


# no active span test
@patch("pylog.logger.logger.trace.get_current_span")
def test_get_otel_context_no_span(mock_span):
    mock_span.return_value = None
    result = get_otel_context()
    assert result == {}


# wrong span context
@patch("pylog.logger.logger.trace.get_current_span")
def test_get_otel_context_invalid_span_context(mock_span):

    fake_span = Mock()
    fake_context = Mock()

    fake_context.is_valid = False

    fake_span.get_span_context.return_value = fake_context
    mock_span.return_value = fake_span

    result = get_otel_context()

    assert result == {}


# valid span context
@patch("pylog.logger.logger.trace.get_current_span")
def test_get_otel_context_valid_span_context(mock_span):

    fake_span = Mock()
    fake_context = Mock()

    fake_context.is_valid = True
    fake_context.trace_id = 123
    fake_context.span_id = 456
    fake_context.trace_flags = 1

    fake_span.get_span_context.return_value = fake_context
    mock_span.return_value = fake_span

    result = get_otel_context()

    assert "trace_id" in result
    assert "span_id" in result
    assert "trace_flags" in result


#  Testing if buidl record contains service name
def test_build_record_contains_service_name():

    logger = Logger(service_name="app-service")

    record = logger.build_record(level="INFO", message="hello")

    assert record["resources"]["attributes"]["service"] == "app-service"


# presence of severity in the record
def test_build_record_contains_severity():

    logger = Logger()

    record = logger.build_record(level="ERROR", message="Something went wrong !")

    assert record["severityText"] == "ERROR"


# presence of the event Name in the record
def test_build_record_contains_event_name():

    logger = Logger()

    record = logger.build_record(level="INFO", message="Hasta la Vista", event_name="user-registration")

    assert record["eventName"] == "user-registration"


# record contains attributes or not
def test_build_record_contains_attributes():
    logger = Logger()

    record = logger.build_record(level="INFO", message="test", user_id=1234)

    assert record["attributes"]["user_id"] == 1234


#  contains base attributes or not
def test_build_record_contains_base_attributes():

    logger = Logger()

    record = logger.build_record(base={"environment": "development"})

    assert record["environment"] == "development"


# check for info
def test_log_calls_structlog_info():

    logger = Logger()

    logger.logger = Mock()

    logger.log(level="INFO", messages="hello")

    logger.logger.info.assert_called_once()


# check for error
def test_log_calls_structlog_error():

    logger = Logger()

    logger.logger = Mock()

    logger.log(level="ERROR", message="something went wrong !!!")

    logger.logger.error.assert_called_once()


# check for calling log info
def test_info_calls_log(mocker):

    logger = Logger()

    sp = mocker.spy(logger, "log")

    logger.info("hello")

    sp.assert_called_once()


# check for calling log error
def test_error_calls_log(mocker):

    logger = Logger()

    sp = mocker.spy(logger, "log")

    logger.error("error")

    sp.assert_called_once()


# check for calling log warn
def test_warn_calls_log(mocker):

    logger = Logger()

    sp = mocker.spy(logger, "log")

    logger.warn("warning")

    sp.assert_called_once()


# check for calling log debug
def test_debug_calls_log(mocker):

    logger = Logger()

    sp = mocker.spy(logger, "log")

    logger.debug("debug")

    sp.assert_called_once()


# checking for whether configure structlog works or not
@patch("pylog.logger.logger.structlog.configure")
def test_configure_structlog(mock_configure):

    configure_structlog()

    mock_configure.assert_called_once()


def test_get_logger_returns_logger():

    logger = get_logger()

    assert isinstance(logger, Logger)


@patch("pylog.logger.logger.configure_structlog")
def test_get_logger_configures_structlog(mock_configure):

    get_logger()

    mock_configure.assert_called_once()


@patch("pylog.logger.logger.tracer")
@pytest.mark.asyncio
async def test_traced_decorator(mock_tracer):

    @traced()
    async def sample_func():
        return "all ok "

    result = await sample_func()

    assert result == "all ok"
    mock_tracer.start_as_current_span.assert_called_once()
