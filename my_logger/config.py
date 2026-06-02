import logging
import os
from logging.handlers import RotatingFileHandler

import structlog

from .processors import add_app_metadata, add_trace_context, mask_sensitive_data
from .settings import JSON_LOGS, LOG_LEVEL


def configure_logger() -> None:

    os.makedirs("logs", exist_ok=True)
    file_handler = RotatingFileHandler(
        filename="logs/app.log", maxBytes=10_000_000, backupCount=5
    )

    console_handler = logging.StreamHandler()

    logging.basicConfig(
        handlers=[console_handler, file_handler], level=LOG_LEVEL, format="%(message)s"
    )

    logging.getLogger("uvicorn.access").disabled = True

    logging.getLogger("uvicorn.access").disabled = True

    logging.getLogger("opentelemetry").setLevel(logging.WARNING)

    renderer = (
        structlog.processors.JSONRenderer(indent=4)
        if JSON_LOGS
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            mask_sensitive_data,
            add_trace_context,
            add_app_metadata,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            renderer,
        ],
        # IMPORTANT FIX
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
