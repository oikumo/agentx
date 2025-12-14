from abc import ABC, abstractclassmethod


class Command(ABC):
    def __init__(self, key: str):
        self.key = key
        pass

    @classmethod
    @abstractclassmethod
    def run(cls, arguments: list[str]):
        pass




