from __future__ import annotations
from agentx.views.rag_view.input_url_view import InputUrlView


class InputUrlController:
    url: str | None

    def __init__(self):
        self.view = InputUrlView(self)
        self.url = None

    def show(self):
        self.view.show()

    def set_url(self, url: str | None):
        self.url = url
