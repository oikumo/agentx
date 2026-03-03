import unittest

from agent_x.app.agent_x import AgentX

class AgentXTest(unittest.TestCase):
    def test_run(self):
        agentx = AgentX()
        agentx.configure()

        assert(True)