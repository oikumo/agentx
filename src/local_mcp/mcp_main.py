import asyncio
import pprint
from typing import TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent, AgentState
from mcp import ClientSession, StdioServerParameters, stdio_client

load_dotenv()

stdio_server_params = StdioServerParameters(
    command="python",
    args=["servers_stdio/math_server.py"],
)

class AgentInput(TypedDict):
    messages: list[BaseMessage]

async def main():
    llm = ChatOpenAI(model="gpt-3.5-turbo") #get_llama_cpp_llm()

    async with stdio_client(stdio_server_params) as (read,write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            await session.initialize()
            pprint.pprint("session initialized")
            tools = await load_mcp_tools(session)

            for tool in tools:
                pprint.pprint(tool.name)

            # Langraph react agent
            agent = create_agent(
                model= llm,
                tools= tools,
                system_prompt= SystemMessage("You are a helpful assistant. Be concise and accurate.")
            )

            result = await agent.ainvoke({"messages": [HumanMessage(content="What is 54 + 2 * 3?")]})
            pprint.pprint(result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())

