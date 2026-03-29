from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode

SYSTEM_MESSAGE = """
You are a helpful assistant that can use tools to answer questions.
"""

def run_agent_reasoning(state: MessagesState) -> MessagesState:
    """
    Run the agent reasoning node.
    """
    llm, tools = get_llm_and_tools()
    response = llm.invoke(
        [{"role": "system", "content": SYSTEM_MESSAGE}, *state["messages"]]
    )
    return {"messages": [response]}


tool_node = ToolNode([])  # Will be initialized properly in the graph