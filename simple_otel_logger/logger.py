from typing import Optional, Any
import structlog

from .logger_interface import Logger


class ConsoleLogger(Logger):
    def __init__(self, service_name: Optional[str] = None):
        super().__init__(service_name)

        base_logger = structlog.get_logger()

        if self.service_name:
            base_logger = base_logger.bind(service=self.service_name)

        self.logger = base_logger

    def _log(self, level: str, message: str, data: Any = None) -> None:
        log_method = getattr(self.logger, level, None)

        if not log_method:
            raise ValueError(f"Invalid log level: {level}")

        log_method(message, data=data)

    def info(self, message: str, data: Any = None) -> None:
        self._log("info", message, data)

    def error(self, message: str, data: Any = None) -> None:
        self._log("error", message, data)

    def warn(self, message: str, data: Any = None) -> None:
        self._log("warning", message, data)  # correct level

    def debug(self, message: str, data: Any = None) -> None:
        self._log("debug", message, data)
