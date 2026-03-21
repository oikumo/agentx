from dotenv import load_dotenv
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode

from llm_factory import LLMFactory
from app.configuration.configuration import (
    AgentXConfiguration,
    LLMConfig,
    LLMProvider,
)

load_dotenv()

SYSYEM_MESSAGE = """
You are a helpful assistant that can use tools to answer questions.
"""


def get_llm_and_tools():
    """Get LLM and tools for the graph."""
    from modules.llm.langgraph.graph_simple.react import tools

    # Initialize LLM configuration and factory
    config = AgentXConfiguration()
    # Add default configurations if not present
    if config.get_llm_config("qwen3:1.7b") is None:
        config.add_llm_config(
            LLMConfig(
                name="qwen3:1.7b",
                provider=LLMProvider.OLLAMA,
                model_name="qwen3:1.7b",
                temperature=0,
                extra_params={"reasoning": True},
            )
        )
    factory = LLMFactory(config)
    llm = factory.get_chat_model("qwen3:1.7b")
    return llm, tools


def run_agent_reasoning(state: MessagesState) -> MessagesState:
    """
    Run the agent reasoning node.
    """
    llm, tools = get_llm_and_tools()
    response = llm.invoke(
        [{"role": "system", "content": SYSYEM_MESSAGE}, *state["messages"]]
    )
    return {"messages": [response]}


tool_node = ToolNode([])  # Will be initialized properly in the graph
