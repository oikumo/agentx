from abc import abstractmethod, ABC


class CommandBase(ABC):
    def __init__(self):
        self.name = "controller"
        self.key = ""
    @abstractmethod
    def run(self, arguments:list):
        pass
