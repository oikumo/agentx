from abc import abstractmethod, ABC
from typing import Protocol


class IMainController(Protocol):
    @abstractmethod
    def close(self) -> None: ...
