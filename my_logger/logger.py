import structlog

from .settings import SERVICE_NAME


def get_logger() -> structlog.BoundLogger:

    return structlog.get_logger().bind(service=SERVICE_NAME)
