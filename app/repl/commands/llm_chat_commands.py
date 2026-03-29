from agents.agent_function_router_factory import create_agent_function_router_local
from agents.agent_rag_factory import create_agent_rag_local
from app.repl.base import IMainController
from app.repl.command import Command
from app.repl.console import Console
from agents.function_tool_router.function_call import QueryRouter
from agents.function_tool_router.functions import get_weather, get_best_game, calculate
from agents.function_tool_router.route import Route
from app_modules.llm.langchain.chat.simple_chat import simple_chat_prompt_template
from app_modules.llm.langchain.react_agents.react_agents_tools.react_tools import react_tools
from app_modules.llm.langchain.react_agents.react_search_agent.search_agent import search_agent
from app_modules.llm.langchain.react_agents.router_agents.router_react_agent import router_agent
from llm_models.local.llama_cpp.llamacpp import LlamaCppConfig
from llm_models.local.llama_cpp_factory import model_factory_llamacpp, LLAMA_CPP_MODEL_QWEN_2_5


class AIFunction(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Run an AI function call demo")

    def run(self, arguments: list[str]) -> None:
        create_agent_function_router_local().function_call()


class AIChat(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Start an AI chat session: chat <query>")

    def run(self, arguments: list[str]) -> None:
        if arguments is None or not arguments:
            Console.log_error("missing args")
            return

        config = LlamaCppConfig()
        config.model_filename = LLAMA_CPP_MODEL_QWEN_2_5
        config.context_size = 32768
        model = model_factory_llamacpp.create_model_instance(config)

        simple_chat_prompt_template(
            llm= model,
            query=" ".join(arguments),
            information="",
        )



class AIRouterAgents(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Run AI router agent")

    def run(self, arguments: list[str]) -> None:
        router_agent()


class AIReactTools(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Run AI ReAct agent with tools")

    def run(self, arguments: list[str]) -> None:
        config = LlamaCppConfig()
        config.model_filename = LLAMA_CPP_MODEL_QWEN_2_5
        config.context_size = 32768
        llm = model_factory_llamacpp.create_model_instance(config)
        react_tools(llm=llm)


class AISearch(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Search the web with AI")

    def run(self, arguments: list[str]) -> None:
        config = LlamaCppConfig()
        config.model_filename = LLAMA_CPP_MODEL_QWEN_2_5
        config.context_size = 32768
        llm = model_factory_llamacpp.create_model_instance(config)
        search_agent(llm=llm)

class RagPDF(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Query a PDF with RAG: rag <query>")

    def run(self, arguments: list[str]) -> None:
        if arguments is None or not arguments:
            Console.log_warning("missing args")
            return

        create_agent_rag_local().run(query=" ".join(arguments))