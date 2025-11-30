from typing import Any

from langchain_classic import hub
from langchain_classic.agents import create_react_agent, AgentExecutor

from langchain_experimental.tools import PythonREPLTool

from src.ai.llm.llms import get_local_llm_qwen3

def create_qr_react_agent_executor():
    print("create_qr_generator_agent_executor")

    instructions = """You are an agent designed to write and execute python code to answer questions.
    You have access to a python REPL, which you can use to execute python code.
    You have qrcode package installed
    If you get an error, debug your code and try again.
    Only use the output of your code to answer the question. 
    You might know the answer without running any code, but you should still run the code to get the answer.
    If it does not seem like you can write code to answer the question, just return "I don't know" as the answer.
        """
    base_prompt = hub.pull("langchain-ai/react-agent-template")
    prompt = base_prompt.partial(instructions=instructions)

    tools = [PythonREPLTool()]
    python_agent = create_react_agent(
        prompt=prompt,
        llm= get_local_llm_qwen3(),
        tools=tools,
    )

    python_agent_executor = AgentExecutor(agent=python_agent, tools=tools, verbose=True)

    return python_agent_executor
