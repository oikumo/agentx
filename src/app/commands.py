from __future__ import annotations

from app.repl import Command, CommandResult, MainController
from app.console import Console
from app.utils import clear_console, safe_int


class CommandResultLogInfo(CommandResult):
    def __init__(self, messages: list[str]):
        self._messages = messages

    def apply(self):
        for message in self._messages:
            Console.log_info(message)


class CommandResultPrint(CommandResult):
    def __init__(self, message: str):
        self._message = message

    def apply(self):
        Console.log_info(self._message)


class QuitCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Exit Agent-X")
        self.controller = controller

    def run(self, arguments: list[str]):
        Console.log_info("QUIT COMMAND")
        self.controller.close()


class ClearCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Clear the output screen")
        self.controller = controller

    def run(self, arguments: list[str]):
        clear_console()


class HelpCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Show available commands")
        self.controller = controller

    def run(self, arguments: list[str]):
        commands: list[str] = []
        for command in self.controller.get_commands():
            commands.append(f"{command.key} - {command.description}")
        return CommandResultLogInfo(commands)


class ReadFile(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Read and display a file: read <filename>")
        self.controller = controller

    def run(self, arguments: list[str]):
        if not arguments:
            Console.log_info("Usage: read <filename>")
            return
        filename = arguments[0]
        try:
            with open(filename, "r") as file:
                content = file.read()
            Console.log_info(content)
        except FileNotFoundError:
            Console.log_info(f"File not found: {filename}")
        except OSError as e:
            Console.log_info(f"Error reading file: {e}")


class SumCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Add two integers: sum <a> <b>")
        self.controller = controller

    def run(self, arguments: list[str]):
        match arguments:
            case (x, y):
                if safe_int(x) is not None and safe_int(y) is not None:
                    result = str(int(x) + int(y))
                    return CommandResultPrint(result)
                else:
                    Console.log_warning("invalid params for sum command")
            case _:
                Console.log_warning("invalid command")
        return None


def parse_chat_arguments(arguments: list[str]) -> tuple[str | None, str]:
    model: str | None = None
    query_parts: list[str] = []
    i = 0
    while i < len(arguments):
        if arguments[i] == "--model":
            if i + 1 < len(arguments):
                model = arguments[i + 1]
                i += 2
            else:
                i += 1
        else:
            query_parts.append(arguments[i])
            i += 1
    query = " ".join(query_parts)
    return model, query


class AISearch(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(
            key, description="Search the web with an React Web Search Agent"
        )
        self.controller = controller

    def run(self, arguments: list[str]) -> None:
        from llm_managers.factory import AgentFactory

        AgentFactory.create_react_web_search().run()


class AIFunction(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Run an AI function call demo")
        self.controller = controller

    def run(self, arguments: list[str]) -> None:
        from llm_managers.factory import AgentFactory

        AgentFactory.create_function_router().function_call()


class AIChat(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(
            key,
            description="Start an AI chat session: chat <query>, chat --model <model> <query>, or chat (interactive loop)",
        )
        self.controller = controller

    def run(self, arguments: list[str]) -> None:
        from llm_managers.factory import AgentFactory
        from llm_managers.providers.openrouter_provider import OpenRouterProvider

        model_name, query = parse_chat_arguments(arguments)

        if model_name:
            provider = OpenRouterProvider(model_name=model_name)
            chat_loop = AgentFactory.create_chat_loop(provider=provider)
        else:
            chat_loop = AgentFactory.create_chat_loop()

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
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Query a PDF with RAG: rag <query>")
        self.controller = controller

    def run(self, arguments: list[str]) -> None:
        from llm_managers.factory import AgentFactory

        if arguments is None or not arguments:
            Console.log_info(
                "Starting interactive RAG chat (type 'quit' or 'exit' to end):"
            )
            chat_loop = AgentFactory.create_chat_loop_rag()
            chat_loop.start_interactive_streaming()
            return

        chat_loop = AgentFactory.create_chat_loop_rag()
        query = " ".join(arguments)
        try:
            response, metrics = chat_loop.run_streaming_with_metrics(query)
            if response is not None:
                print()
                Console.log_info(metrics.format())
        except Exception as e:
            Console.log_error(f"RAG error: {e}")


class AIRouterAgents(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Run AI router agent")
        self.controller = controller

    def run(self, arguments: list[str]) -> None:
        from app_modules.llm.langchain.react_agents.router_agents.router_react_agent import (
            router_agent,
        )

        router_agent()


class AIReactTools(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Run AI ReAct agent with tools")
        self.controller = controller

    def run(self, arguments: list[str]) -> None:
        from llm_models.local.llama_cpp.llamacpp import LlamaCppConfig
        from llm_models.local.llama_cpp_factory import (
            model_factory_llamacpp,
            LLAMA_CPP_MODEL_QWEN_2_5,
        )
        from app_modules.llm.langchain.react_agents.react_agents_tools.react_tools import (
            react_tools,
        )

        config = LlamaCppConfig()
        config.model_filename = LLAMA_CPP_MODEL_QWEN_2_5
        config.context_size = 32768
        llm = model_factory_llamacpp.create_model_instance(config)
        react_tools(llm=llm)


class AIGraphSimple(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Run a simple LangGraph workflow")
        self.controller = controller

    def run(self, arguments: list[str]):
        from llm_managers.factory import AgentFactory
        from llm_managers.providers.openai_provider import OpenAIProvider

        AgentFactory.create_graph_react_web_search(provider=OpenAIProvider()).run()


class AIGraphChains(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Run a LangGraph reflector chains graph")
        self.controller = controller

    def run(self, arguments: list[str]):
        from app_modules.llm.langgraph.graph_reflector_chain.graph_chains import (
            graph_chains,
        )

        graph_chains()


class AIGraphReflexion(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Run a LangGraph reflexion agent")
        self.controller = controller

    def run(self, arguments: list[str]):
        from app_modules.llm.langgraph.graph_reflexion_agent.graph_reflexion_agent import (
            graph_reflexion_agent,
        )

        graph_reflexion_agent()
