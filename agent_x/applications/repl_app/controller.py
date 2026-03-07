from abc import ABC


class Controller(ABC):
    def __init__(self, name: str, key: str):
        if not (name and name.strip()):
            raise ValueError("Session name cannot be empty or whitespace")
        self._name = name.strip()

    def name(self):
        return self._name
