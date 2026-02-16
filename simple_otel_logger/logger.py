import json
from datetime import datetime
from typing import Optional, Any, Dict

from opentelemetry import trace

from logger_interface import Logger


class ConsoleLogger(Logger):
    def __init__(self, service_name: Optional[str] = None):
        super().__init__(service_name)

    def _get_otel_context(self) -> Dict[str, str]:
        span = trace.get_current_span()

        if not span:
            return {}

        ctx = span.get_span_context()

        if not ctx or not ctx.trace_id:
            return {}

        return {
            "traceId": format(ctx.trace_id, "032x"),
            "spanId": format(ctx.span_id, "016x"),
        }

    def _log(self, level: str, message: str, data: Any = None) -> None:
        record = {
            "level": level,
            "message": message,
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat(),
            **self._get_otel_context(),
            "data": data,
        }

        print(json.dumps(record))

    def info(self, message: str, data: Any = None) -> None:
        self._log("info", message, data)

    def error(self, message: str, data: Any = None) -> None:
        self._log("error", message, data)

    def warn(self, message: str, data: Any = None) -> None:
        self._log("warn", message, data)

    def debug(self, message: str, data: Any = None) -> None:
        self._log("debug", message, data)
