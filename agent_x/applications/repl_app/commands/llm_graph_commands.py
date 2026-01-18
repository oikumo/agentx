from agent_x.applications.repl_app.command_line_controller.command import Command
from agent_x.modules.llm.langgraph.graph_reflector_chain.graph_chains import graph_chains
from agent_x.modules.llm.langgraph.graph_reflexion_agent.graph_reflexion_agent import graph_reflexion_agent
from agent_x.modules.llm.langgraph.graph_simple.graph_simple import graph_simple


class AIGraphSimple(Command):
    def __init__(self, key: str):
        super().__init__(key)
    def run(self, arguments: list[str]):
        graph_simple()

class AIGraphChains(Command):
    def run(self, arguments: list[str]):
        graph_chains()

class AIGraphReflexion(Command):
    def run(self, arguments: list[str]):
        graph_reflexion_agent()