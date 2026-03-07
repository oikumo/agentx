from abc import ABC, abstractmethod


class Command(ABC):
    def __init__(self, key: str):
        self.key = key

    @abstractmethod
    def run(self, arguments: list[str]):
        pass
