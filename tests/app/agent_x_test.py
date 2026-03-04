import unittest

from agent_x.app.agent_x import AgentX
from agent_x.common.logger import log_info


class AgentXTest(unittest.TestCase):
    def test_run(self):
        agentx = AgentX()
        log_info(",".join(agentx.llms))
        agentx.configure()
        log_info(",".join(agentx.llms))
        agentx.configure()
        log_info(",".join(agentx.llms))

        assert(True)