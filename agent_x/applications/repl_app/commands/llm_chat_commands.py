from langchain_classic import hub
from langchain_ollama import OllamaEmbeddings

from agent_x.llm_models.local.llms import (
    get_llama_cpp_llm,
    get_local_llm_qwen2_5,
    get_local_llm_qwen3,
)
from agent_x.modules.data_stores.faiss_rag.rag_pdf.rag_pdf import rag_pdf
from agent_x.applications.repl_app.command_line_controller.command import Command
from agent_x.modules.llm.functions.function_call import function_call
from agent_x.modules.llm.langchain.chat.simple_chat import simple_chat_prompt_template
from agent_x.modules.llm.langchain.react_agents.react_agents_tools.react_tools import (
    react_tools,
)
from agent_x.modules.llm.langchain.react_agents.react_search_agent.search_agent import (
    search_agent,
)
from agent_x.modules.llm.langchain.react_agents.router_agents.router_react_agent import (
    router_agent,
)
from agent_x.modules.llm.langchain.tools.simple_tool import simple_tool
from agent_x.common.logger import log_warning


class AIFunction(Command):
    def __init__(self, key: str):
        super().__init__(key, description="Run an AI function call demo")

    def run(self, arguments: list[str]) -> None:
        function_call()


class AIChat(Command):
    def __init__(self, key: str):
        super().__init__(key, description="Start an AI chat session: chat <query>")

    def run(self, arguments: list[str]) -> None:
        if arguments is None or not arguments:
            log_warning("missing args")
            return
        simple_chat_prompt_template(
            llm=get_llama_cpp_llm(),
            query=" ".join(arguments),
            information="consider all games like dark souls",
        )


class AITools(Command):
    def __init__(self, key: str):
        super().__init__(key, description="Run AI agent with tool use")

    def run(self, arguments: list[str]) -> None:
        simple_tool(llm=get_local_llm_qwen2_5())


class AIRouterAgents(Command):
    def __init__(self, key: str):
        super().__init__(key, description="Run AI router agent")

    def run(self, arguments: list[str]) -> None:
        router_agent()


class AIReactTools(Command):
    def __init__(self, key: str):
        super().__init__(key, description="Run AI ReAct agent with tools")

    def run(self, arguments: list[str]) -> None:
        react_tools(llm=get_local_llm_qwen2_5())


class AISearch(Command):
    def __init__(self, key: str):
        super().__init__(key, description="Search the web with AI")

    def run(self, arguments: list[str]) -> None:
        search_agent(llm=get_local_llm_qwen2_5())


class RagPDF(Command):
    def __init__(self, key: str):
        super().__init__(key, description="Query a PDF with RAG: rag <query>")

    def run(self, arguments: list[str]) -> None:
        if arguments is None or not arguments:
            log_warning("missing args")
            return
        rag_pdf(
            query=" ".join(arguments),
            pdf_path="/resources/react.pdf",
            vectorstore_path="/local/faiss_index_react",
            retrieval_qa_chat_prompt=hub.pull("langchain-ai/retrieval-qa-chat"),
            llm=get_local_llm_qwen3(),
            embeddings=OllamaEmbeddings(model="nomic-embed-text"),
        )
