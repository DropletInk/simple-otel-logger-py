from typing import Any, Dict, TypedDict
class LogRecord(TypedDict, total=False):
    level: str
    message: str
    event_name: str
    timestamp: str
    attributes: Dict[str, Any]


class LoggerOptions(TypedDict, total=False):
    service_name: str
    environment: str
