from agent_x.app.ai.graph_reflector_chain.graph_chains import graph_chains
from agent_x.app.ai.graph_simple.graph_simple import graph_simple
from agent_x.core.controllers.command_line_controller.command import Command

class AIGraphSimple(Command):
    def __init__(self, key: str):
        super().__init__(key)
    def run(self, arguments: list[str]):
        graph_simple()

class AIGraphChains(Command):
    def run(self, arguments: list[str]):
        graph_chains()