from enum import IntEnum
from abc import ABC, abstractmethod
from dataclasses import dataclass

class UIMessageType(IntEnum):
    INFO = 0
    SUCCESS = 1
    WARNING = 2
    ERROR = 3
    HEADER = 4


@dataclass
class UIMessage:
    message: str
    message_type: UIMessageType = UIMessageType.INFO


class UIConsoleBase(ABC):
    lines: list[UIMessage]

    @abstractmethod
    def print_now(self, message: str) -> None: ...

    @abstractmethod
    def print_line(self, line: UIMessage) -> None : ...

    @abstractmethod
    def capture_input(self) -> str | None: ...

    def __init__(self):
        self.lines = []

    def info(self, message: str) -> UIConsoleBase:
        self.lines.append(UIMessage(message, UIMessageType.INFO))
        return self

    def waning(self, message: str) -> UIConsoleBase:
        self.lines.append(UIMessage(message, UIMessageType.WARNING))
        return self

    def success(self, message: str) -> UIConsoleBase:
        self.lines.append(UIMessage(message, UIMessageType.SUCCESS))
        return self

    def error(self, message: str) -> UIConsoleBase:
        self.lines.append(UIMessage(message, UIMessageType.ERROR))
        return self

    def header(self, message: str) -> UIConsoleBase:
        self.lines.append(UIMessage(message, UIMessageType.HEADER))
        return self

    def flush(self):
        for line in self.lines:
            self.print_line(line)
        self.lines.clear()
