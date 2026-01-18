from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from agent_x.modules.ai.langgraph.graph_reflexion_agent.schemas import AnswerQuestion, ReviseAnswer

load_dotenv()

from langchain_core.tools import StructuredTool

from langgraph.prebuilt import ToolNode

tavily_tool = TavilySearch(max_results=5)


def run_queries(search_queries: list[str], **kwargs):
    """Run the generated queries."""
    return tavily_tool.batch([{"query": query} for query in search_queries])


execute_tools = ToolNode(
    [
        StructuredTool.from_function(run_queries, name=AnswerQuestion.__name__),
        StructuredTool.from_function(run_queries, name=ReviseAnswer.__name__),
    ]
)
