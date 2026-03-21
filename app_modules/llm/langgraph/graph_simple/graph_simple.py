from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, MessagesState, StateGraph

from app_modules.llm.langgraph.graph_simple.nodes import get_llm_and_tools, run_agent_reasoning

load_dotenv()

AGENT_REASON = "agent_reason"
ACT = "act"
LAST = -1


def should_continue(state: MessagesState) -> str:
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


def graph_simple():
    print(f"graph simple")
    print("Hello ReAct LangGraph with Function Calling")
    flow = StateGraph(MessagesState)

    # Get LLM and tools
    llm, tools = get_llm_and_tools()

    # Update the tool_node with actual tools
    from langgraph.prebuilt import ToolNode

    tool_node = ToolNode(tools)

    flow.add_node(AGENT_REASON, run_agent_reasoning)
    flow.set_entry_point(AGENT_REASON)
    flow.add_node(ACT, tool_node)

    flow.add_conditional_edges(AGENT_REASON, should_continue, {END: END, ACT: ACT})

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
