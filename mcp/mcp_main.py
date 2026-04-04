import asyncio
import pprint
from typing import TypedDict

import openai
from dotenv import load_dotenv
from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent, AgentState
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

stdio_server_params = StdioServerParameters(
    command="python",
    args=["/home/oikumo/develop/projects/mcp-docker-x/servers/math_server.py"],
)

class AgentInput(TypedDict):
    messages: list[BaseMessage]

async def main():
    llm = ChatOpenAI(model="gpt-3.5-turbo") #get_llama_cpp_llm()

    async with stdio_client(stdio_server_params) as (read,write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            await session.initialize()
            print("session initialized")
            tools = await load_mcp_tools(session)

            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are helpful."),
                ("human", "{input}")
            ])

            # Langraph react agent
            agent = create_agent(
                model= llm,
                tools= tools,
                system_prompt= "You are a helpful assistant. Be concise and accurate."
            )

            result = await agent.ainvoke({"messages": [HumanMessage(content="What is 54 + 2 * 3?")]})
            pprint.pprint(result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())

