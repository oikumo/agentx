from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

from llm_factory import LLMFactory
from app.configuration.configuration import (
    AgentXConfiguration,
    LLMConfig,
    LLMProvider,
)

load_dotenv()


@tool
def triple(num: float) -> float:
    """
    param num: a number to triple
    returns: the triple of the input number
    """
    return float(num) * 3


# Initialize LLM configuration and factory
def get_llm():
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
    return factory.get_chat_model("qwen3:1.7b")


tools = [TavilySearch(max_results=1), triple]

llm = get_llm().bind_tools(tools)
