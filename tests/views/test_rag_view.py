import unittest

from agentx.views.rag_view.rag_view import RagView
from agentx.views.ui.ui import UIConsoleBase, UIMessage


class TestRagView(unittest.TestCase):
    def test_show(self):
        class Console(UIConsoleBase):
            def print_line(self, line: UIMessage) -> None:
                assert line.message == "RAG"

        view = RagView(Console())
        view.show()
