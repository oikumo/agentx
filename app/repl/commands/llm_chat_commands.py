from llm_managers.agent_chat_factory import (
    create_agent_chat_local,
    create_chat_loop_local,
    create_chat_loop_with_model,
)
from llm_managers.agent_function_router_factory import (
    create_agent_function_router_local,
)
from llm_managers.agent_rag_factory import create_agent_rag_local
from llm_managers.agent_react_web_search_factory import (
    create_agent_react_web_search_local,
)
from app.repl.base import IMainController
from app.repl.command import Command
from app.repl.console import Console
from app.repl.utils.argument_parser import parse_chat_arguments
from app_modules.llm.langchain.react_agents.react_agents_tools.react_tools import (
    react_tools,
)
from app_modules.llm.langchain.react_agents.router_agents.router_react_agent import (
    router_agent,
)
from llm_models.local.llama_cpp.llamacpp import LlamaCppConfig
from llm_models.local.llama_cpp_factory import (
    model_factory_llamacpp,
    LLAMA_CPP_MODEL_QWEN_2_5,
)


class AISearch(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(
            key, controller, description="Search the web with an React Web Search Agent"
        )

    def run(self, arguments: list[str]) -> None:
        create_agent_react_web_search_local().run()


class AIFunction(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Run an AI function call demo")

    def run(self, arguments: list[str]) -> None:
        create_agent_function_router_local().function_call()


class AIChat(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(
            key,
            controller,
            description="Start an AI chat session: chat <query>, chat --model <model> <query>, or chat (interactive loop)",
        )

    def run(self, arguments: list[str]) -> None:
        model_name, query = parse_chat_arguments(arguments)

        if model_name:
            chat_loop = create_chat_loop_with_model(model_name)
        else:
            chat_loop = create_chat_loop_local()

        if not query:
            Console.log_info(
                "Starting interactive chat (type 'quit' or 'exit' to end):"
            )
            chat_loop.start_interactive_streaming()
        else:
            try:
                response, metrics = chat_loop.run_streaming_with_metrics(query)
                if response is not None:
                    print()
                    Console.log_info(metrics.format())
            except Exception as e:
                Console.log_error(f"Chat error: {e}")


class RagPDF(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(
            key, controller, description="Query a PDF with RAG: rag <query>"
        )

    def run(self, arguments: list[str]) -> None:
        if arguments is None or not arguments:
            Console.log_warning("missing args")
            return

        create_agent_rag_local().run(query=" ".join(arguments))


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
