from agent_x.app.ai.graph_simple.graph_simple import graph_simple
from agent_x.app.llm.llms import get_llama_cpp_llm, get_local_llm_qwen2_5, get_local_llm_qwen3
from agent_x.core.controllers.command_line_controller.command import Command

class AIGraphSimple(Command):
    def __init__(self, key: str):
        super().__init__(key)
    def run(self, arguments: list[str]):
        graph_simple(llm=get_llama_cpp_llm())