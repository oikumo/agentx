from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

from agent_x.llm_models.local.llms import get_local_llm_qwen3

load_dotenv()


@tool
def triple(num: float) -> float:
    """
    param num: a number to triple
    returns: the triple of the input number
    """
    return float(num) * 3


tools = [TavilySearch(max_results=1), triple]

llm = get_local_llm_qwen3().bind_tools(tools)
