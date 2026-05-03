import unittest

from agentx.model.rag import Rag


class TestRag(unittest.TestCase):
    def test_something(self):
        rag = Rag()
        rag.setup()
        self.assertEqual(True, True)  # add assertion here
