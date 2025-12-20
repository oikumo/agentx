from abc import abstractmethod, ABC, abstractclassmethod
from typing import Protocol


class IMainController(Protocol):
    @classmethod
    @abstractmethod
    def close(self) -> None:
        ...