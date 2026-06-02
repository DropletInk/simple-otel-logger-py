from .config import configure_logger
from .logger import get_logger as get_logger
from .metrics import router as metrics_router
from .middleware import LoggingMiddleware
from .telemetry import setup_tracing


def setup_metrics(app):
    app.include_router(metrics_router)


configure_logger()

LoggingMiddleware()
setup_tracing()
