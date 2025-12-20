from agent_x.app.llm.llms import get_llama_cpp_llm, get_local_llm_qwen2_5
from agent_x.app.ai.agent_tools.simple_tool import simple_tool
from agent_x.app.ai.chat.simple_chat import simple_chat_prompt_template
from agent_x.app.ai.react_agents_tools.react_tools import react_tools
from agent_x.app.ai.react_search_agent.search_agent import search_agent
from agent_x.app.ai.router_agents.router_react_agent import router_agent
from agent_x.core.controllers.command_line_controller.command import Command


class AIChat(Command):
    def __init__(self, key: str):
        super().__init__(key)
    def run(self, arguments: list[str]):
        if arguments is None or not arguments:
            print("missing args")
            return
        simple_chat_prompt_template(
            llm=get_llama_cpp_llm(),
            query= " ".join(arguments),
            information="consider all games like dark souls")

class AITools(Command):
    def run(cls, arguments: list[str]):
        simple_tool(llm=get_local_llm_qwen2_5())


class AIRouterAgents(Command):
    def run(cls, arguments: list[str]):
        router_agent()

class AIReactTools(Command):
    def run(cls, arguments: list[str]):
        react_tools(llm=get_local_llm_qwen2_5())

class AISearch(Command):
    def run(cls, arguments: list[str]):
        search_agent(llm=get_local_llm_qwen2_5())