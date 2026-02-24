from abc import ABC, abstractmethod
from typing import Any, Optional


class Logger(ABC):
    def __init__(self, service_name: Optional[str] = None):
        self.service_name = service_name

    @abstractmethod
    def _log(self, level: str, message: str, data: Any = None) -> None:
        pass

    @abstractmethod
    def info(self, message: str, data: Any = None) -> None:
        pass

    @abstractmethod
    def error(self, message: str, data: Any = None) -> None:
        pass

    @abstractmethod
    def warn(self, message: str, data: Any = None) -> None:
        pass

    @abstractmethod
    def debug(self, message: str, data: Any = None) -> None:
        pass
