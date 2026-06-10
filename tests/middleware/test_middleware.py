import pytest
from unittest.mock import Mock, AsyncMock

from starlette.requests import Request
from starlette.responses import Response

from pylog.middleware.middleware import LoggingMiddleware


# Hel per function
def create_request(headers=None):
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": headers or [],
    }

    return Request(scope)


@pytest.mark.asyncio
async def test_request_log_generated():

    logger = Mock()

    middleware = LoggingMiddleware(
        app=Mock(),
        logger=logger,
    )

    request = create_request()

    response = Response(status_code=200)

    call_next = AsyncMock(return_value=response)

    await middleware.dispatch(
        request,
        call_next,
    )

    assert logger.info.called


@pytest.mark.asyncio
async def test_response_log_generated():

    logger = Mock()

    middleware = LoggingMiddleware(
        app=Mock(),
        logger=logger,
    )

    request = create_request()

    response = Response(status_code=200)

    call_next = AsyncMock(return_value=response)

    await middleware.dispatch(
        request,
        call_next,
    )

    assert logger.info.call_count == 2


@pytest.mark.asyncio
async def test_error_log_for_server_error():

    logger = Mock()

    middleware = LoggingMiddleware(
        app=Mock(),
        logger=logger,
    )

    request = create_request()

    response = Response(status_code=500)

    call_next = AsyncMock(return_value=response)

    await middleware.dispatch(
        request,
        call_next,
    )

    logger.error.assert_called_once()
