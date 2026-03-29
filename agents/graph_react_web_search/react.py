from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
from langchain_tavily import TavilySearch


@tool
def triple(num: float) -> float:
    """
    param num: a number to triple
    returns: the triple of the input number
    """
    return float(num) * 3

class GraphReact:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def run(self):
        tools = [TavilySearch(max_results=1), triple]
        llm = self.llm.bind_tools(tools)
