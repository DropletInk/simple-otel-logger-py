from typing import Any, Dict, TypedDict
from enum import IntEnum


class LogRecord(TypedDict, total=False):
    level: str
    message: str
    event_name: str
    timestamp: str
    attributes: Dict[str, Any]


class LoggerOptions(TypedDict, total=False):
    service_name: str
    environment: str


class Severity(IntEnum):
    DEBUG = 5
    INFO = 9
    WARN = 13
    ERROR = 17
