from pathlib import Path

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_tavily import TavilySearch
from langgraph.constants import END
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool


load_dotenv()

AGENT_REASON = "agent_reason"
ACT = "act"
LAST = -1

SYSTEM_MESSAGE = """
You are a helpful assistant that can use tools to answer questions.
"""

@tool
def triple(num: float) -> float:
    """
    param num: a number to triple
    returns: the triple of the input number
    """
    return float(num) * 3

class GraphReactWebSearch:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.tool_node = ToolNode([])  # Will be initialized properly in the graph
        tools = [TavilySearch(max_results=1), triple]
        self.llm_full = self.llm.bind_tools(tools)

    def run_agent_reasoning(self, state: MessagesState) -> MessagesState:
        """
        Run the agent reasoning node.
        """
        llm, tools = self.llm_full
        response = llm.invoke(
            [{"role": "system", "content": SYSTEM_MESSAGE}, *state["messages"]]
        )
        return {"messages": [response]}



    def should_continue(self, state: MessagesState) -> str:
        last_message = state["messages"][LAST]
        # Check if the last message has tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return ACT
        # Also check for tool_calls in additional_kwargs (common in some message types)
        if (
            hasattr(last_message, "additional_kwargs")
            and "tool_calls" in last_message.additional_kwargs
        ):
            return ACT
        return END


    def graph_simple(self):
        print(f"graph simple")
        print("Hello ReAct LangGraph with Function Calling")

        flow = StateGraph(MessagesState)

        # Get LLM and tools
        llm, tools = self.llm_full

        # Update the tool_node with actual tools
        from langgraph.prebuilt import ToolNode

        tool_node = ToolNode(tools)

        flow.add_node(AGENT_REASON, self.run_agent_reasoning)
        flow.set_entry_point(AGENT_REASON)
        flow.add_node(ACT, tool_node)

        flow.add_conditional_edges(AGENT_REASON, self.should_continue, {END: END, ACT: ACT})

        flow.add_edge(ACT, AGENT_REASON)

        local_path = Path.cwd() / "local"
        print(f"WWWWWWWWWWWWWWWW: {local_path}")

        app = flow.compile()
        app.get_graph().draw_mermaid_png(output_file_path="local/flow.png")

        res = app.invoke(
            {
                "messages": [
                    HumanMessage(
                        content="What is the temperature in Tokyo? List it and then triple it"
                    )
                ]
            }
        )
        print(res["messages"][LAST].content)