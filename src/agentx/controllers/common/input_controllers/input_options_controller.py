from __future__ import annotations

from agentx.controllers.common.input_controllers.input_options_view import InputOptionsView


class InputOptionsController:
    options: dict[int, str]
    selected_option = int | None

    def __init__(self, options: dict[int, str]):
        self.view = InputOptionsView(self, options)
        self.url = None

    def show(self) -> None:
        self.view.show()

    def set_option(self, option: int | None) -> None:
        self.selected_option = option

    def get_option(self) ->  int | None:
        return self.selected_option
