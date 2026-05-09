import unittest

from agentx.controllers.rag_controller.rag_controller import RagController
from agentx.views.rag_view.rag_view import RagView
from agentx.views.ui.ui import UIConsoleBase, UIMessage


class TestRagController(unittest.TestCase):
    def test_something(self):
        class Console(UIConsoleBase):
            def print_line(self, line: UIMessage) -> None:
                pass

        rag = RagController(RagView(Console()))
        rag.show()


