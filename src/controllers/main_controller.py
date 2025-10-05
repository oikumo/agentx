from src.controllers.base_controller import BaseController


class MainController(BaseController):
    def info(self) -> str:
        return "main"