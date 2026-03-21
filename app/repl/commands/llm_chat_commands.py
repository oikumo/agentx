from langchain_classic import hub

from app.repl.base import IMainController
from app.repl.command import Command
from app.configuration.configuration import (
    AgentXConfiguration,
)
from app.repl.console import Console
from app_modules.data_stores.rag_pdf import rag_pdf
from app_modules.llm.functions.function_call import QueryRouter
from app_modules.llm.functions.functions import get_weather, get_best_game, calculate
from app_modules.llm.functions.route import Route
from app_modules.llm.langchain.chat.simple_chat import simple_chat_prompt_template
from app_modules.llm.langchain.react_agents.react_agents_tools.react_tools import react_tools
from app_modules.llm.langchain.react_agents.react_search_agent.search_agent import search_agent
from app_modules.llm.langchain.react_agents.router_agents.router_react_agent import router_agent
from app_modules.llm.langchain.tools.simple_tool import simple_tool
from app_modules.llm_models.llm_factory import LLMFactory


class AIFunction(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Run an AI function call demo")

    def run(self, arguments: list[str]) -> None:
        routes = [
            Route("get_weather", get_weather),
            Route("get_best_game", get_best_game),
            Route("calculate", calculate)
        ]
        router = QueryRouter(routes)
        router.function_call()


class AIChat(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Start an AI chat session: chat <query>")
        # Initialize configuration and factory
        self.config = AgentXConfiguration()
        # Add default configurations if not present
        if self.config.get_llm_config("qwen3:1.7b") is None:
            from app.configuration.configuration import LLMConfig, LLMProvider

            self.config.add_llm_config(
                LLMConfig(
                    name="qwen3:1.7b",
                    provider=LLMProvider.OLLAMA,
                    model_name="qwen3:1.7b",
                    temperature=0,
                    extra_params={"reasoning": True},
                )
            )
        self.factory = LLMFactory(self.config)

    def run(self, arguments: list[str]) -> None:
        if arguments is None or not arguments:
            Console.log_error("missing args")
            return
        simple_chat_prompt_template(
            llm=self.factory.get_chat_model("qwen3:1.7b"),
            query=" ".join(arguments),
            information="consider all games like dark souls",
        )


class AITools(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Run AI agent with tool use")
        # Initialize configuration and factory
        self.config = AgentXConfiguration()
        # Add default configurations if not present
        if self.config.get_llm_config("qwen2.5:1.5b") is None:
            from app.configuration.configuration import LLMConfig, LLMProvider

            self.config.add_llm_config(
                LLMConfig(
                    name="qwen2.5:1.5b",
                    provider=LLMProvider.OLLAMA,
                    model_name="qwen2.5:1.5b",
                    temperature=0,
                    extra_params={"reasoning": False},
                )
            )
        self.factory = LLMFactory(self.config)

    def run(self, arguments: list[str]) -> None:
        simple_tool(llm=self.factory.get_chat_model("qwen2.5:1.5b"))


class AIRouterAgents(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Run AI router agent")

    def run(self, arguments: list[str]) -> None:
        router_agent()


class AIReactTools(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Run AI ReAct agent with tools")
        # Initialize configuration and factory
        self.config = AgentXConfiguration()
        # Add default configurations if not present
        if self.config.get_llm_config("qwen2.5:1.5b") is None:
            from app.configuration.configuration import LLMConfig, LLMProvider

            self.config.add_llm_config(
                LLMConfig(
                    name="qwen2.5:1.5b",
                    provider=LLMProvider.OLLAMA,
                    model_name="qwen2.5:1.5b",
                    temperature=0,
                    extra_params={"reasoning": False},
                )
            )
        self.factory = LLMFactory(self.config)

    def run(self, arguments: list[str]) -> None:
        react_tools(llm=self.factory.get_chat_model("qwen2.5:1.5b"))


class AISearch(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Search the web with AI")
        # Initialize configuration and factory
        self.config = AgentXConfiguration()
        # Add default configurations if not present
        if self.config.get_llm_config("qwen2.5:1.5b") is None:
            from app.configuration.configuration import LLMConfig, LLMProvider

            self.config.add_llm_config(
                LLMConfig(
                    name="qwen2.5:1.5b",
                    provider=LLMProvider.OLLAMA,
                    model_name="qwen2.5:1.5b",
                    temperature=0,
                    extra_params={"reasoning": False},
                )
            )
        self.factory = LLMFactory(self.config)

    def run(self, arguments: list[str]) -> None:
        search_agent(llm=self.factory.get_chat_model("qwen2.5:1.5b"))


class RagPDF(Command):
    def __init__(self, key: str, controller: IMainController):
        super().__init__(key, controller, description="Query a PDF with RAG: rag <query>")
        # Initialize configuration and factory
        self.config = AgentXConfiguration()
        # Add default configurations if not present
        if self.config.get_llm_config("qwen3:1.7b") is None:
            from app.configuration.configuration import LLMConfig, LLMProvider

            self.config.add_llm_config(
                LLMConfig(
                    name="qwen3:1.7b",
                    provider=LLMProvider.OLLAMA,
                    model_name="qwen3:1.7b",
                    temperature=0,
                    extra_params={"reasoning": True},
                )
            )
        if self.config.get_llm_config("nomic-embed-text") is None:
            from app.configuration.configuration import LLMConfig, LLMProvider

            self.config.add_llm_config(
                LLMConfig(
                    name="nomic-embed-text",
                    provider=LLMProvider.OLLAMA,
                    model_name="nomic-embed-text",
                    temperature=0,
                )
            )
        self.factory = LLMFactory(self.config)

    def run(self, arguments: list[str]) -> None:
        if arguments is None or not arguments:
            Console.log_warning("missing args")
            return
        rag_pdf(
            query=" ".join(arguments),
            pdf_path="/resources/react.pdf",
            vectorstore_path="/local/faiss_index_react",
            retrieval_qa_chat_prompt=hub.pull("langchain-ai/retrieval-qa-chat"),
            llm=self.factory.get_chat_model("qwen3:1.7b"),
            embeddings=self.factory.get_embedding_model("nomic-embed-text"),
        )
