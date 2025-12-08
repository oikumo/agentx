from abc import ABC, abstractclassmethod

class Command(ABC):
    def __init__(self, key:str):
        self.key = key
        pass

class SumCommand(Command):
    def __init__(self, key: str):
        super().__init__(key)

