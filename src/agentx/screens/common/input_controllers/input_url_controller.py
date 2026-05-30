from __future__ import annotations
from agentx.screens.common.input_controllers.input_url_view import InputUrlView


class InputUrlController:
    url: str | None

    def __init__(self):
        self.view = InputUrlView(self)
        self.url = None

    def show(self):
        self.view.show()

    def set_url(self, url: str | None):
        self.url = url
