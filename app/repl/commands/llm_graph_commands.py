from app.repl.base import IMainController
from app.repl.command_line_controller.command import \
    Command
from app_modules.llm.langgraph.graph_reflector_chain.graph_chains import graph_chains
from app_modules.llm.langgraph.graph_reflexion_agent.graph_reflexion_agent import graph_reflexion_agent
from app_modules.llm.langgraph.graph_simple.graph_simple import graph_simple


class AIGraphSimple(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Run a simple LangGraph workflow")

    def run(self, arguments: list[str]):
        graph_simple()


class AIGraphChains(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Run a LangGraph reflector chains graph")

    def run(self, arguments: list[str]):
        graph_chains()


class AIGraphReflexion(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Run a LangGraph reflexion agent")

    def run(self, arguments: list[str]):
        graph_reflexion_agent()
