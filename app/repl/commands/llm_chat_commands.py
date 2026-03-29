from langchain_classic import hub
from ollama import embeddings

from app.repl.base import IMainController
from app.repl.command import Command
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
from llm_models.local.llama_cpp.llamacpp import LlamaCppConfig
from llm_models.local.llama_cpp_factory import model_factory_llamacpp, LLAMA_CPP_MODEL_QWEN_2_5
from llm_models.local.ollama.ollama_embeddings import create_embeddings_model


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

        config = LlamaCppConfig()
        config.model_filename = LLAMA_CPP_MODEL_QWEN_2_5
        config.context_size = 32768
        llm = model_factory_llamacpp.create_model_instance(config)

        ollama_embeddings = create_embeddings_model()

        rag_pdf(
            query=" ".join(arguments),
            pdf_path="/resources/react.pdf",
            vectorstore_path="/local/faiss_index_react",
            retrieval_qa_chat_prompt=hub.pull("langchain-ai/retrieval-qa-chat"),
            llm=llm,
            embeddings=ollama_embeddings,
        )
