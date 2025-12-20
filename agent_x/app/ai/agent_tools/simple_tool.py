from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from agent_x.app.ai.agent_tools.tools.math_tools import multiply

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