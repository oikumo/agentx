from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool


@tool
def multiply(x: float, y: float) -> float:
    """Multiply 'x' times 'y'."""
    return x * y


def simple_tool(llm: BaseLanguageModel):
    print("simple tool")

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "you're a helpful assistant, use the tools provided"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    tools = [multiply]
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)

    res = agent_executor.invoke(
        {
            "input": "create a python program that use the provided tool and test it",
        }
    )
    print(res)
