from unittest.mock import patch, MagicMock
import uuid
import pytest
from pylog.middleware import add_request_id, create_log_middleware


# creating a mopck object for the bind_contextvars
#  to test the the add_request_idf function
@patch("pylog.middleware.middleware.structlog.contextvars.bind_contextvars")
def test_add_request_id(mock_bind):
    request_id = add_request_id()
    assert isinstance(request_id, uuid.UUID)
    mock_bind.assert_called_once_with(request_id=request_id)


#  Testing  the middleware
# using MagicMock for the logger object
@pytest.mark.asyncio
async def test_log_middleware():
    logger = MagicMock()
    request = MagicMock()
    response = MagicMock()

    def request_data(requ):
        return {"path": "/users"}

    def response_data(req, res):
        return {"status_code": 200}

    async def call_next(requ):
        return response

    middleware = create_log_middleware(logger, request_data, response_data)

    res = await middleware(request, call_next)

    assert res == response
