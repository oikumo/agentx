from typing import Any

from dotenv import load_dotenv
from langchain_classic import hub
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from ai.llm.llms import get_local_llm_qwen3
from ai.router_agents.agent_executors.csv_agent import create_csv_agent_executor
from ai.router_agents.agent_executors.qr_react_agent import create_qr_react_agent_executor

load_dotenv()

def router_agent():
    print("router_agent start")

    python_agent_executor = create_qr_react_agent_executor()
    def python_agent_executor_wrapper(original_prompt: str) -> dict[str, Any]:
        return python_agent_executor.invoke({"input": original_prompt})

    csv_agent_executor =create_csv_agent_executor("../resources/episode_info.csv")

    tools = [
        Tool(
            name="Python Agent",
            func=python_agent_executor_wrapper,
            description="""useful when you need to transform natural language to python and execute the python code,
                          returning the results of the code execution
                          DOES NOT ACCEPT CODE AS INPUT""",
        ),
        Tool(
            name="CSV Agent",
            func=csv_agent_executor.invoke,
            description="""useful when you need to answer question over episode_info.csv file,
                         takes an input the entire question and returns the answer after running pandas calculations""",
        ),
    ]

    base_prompt = hub.pull("langchain-ai/react-agent-template")
    prompt = base_prompt.partial(instructions="")
    grand_agent = create_react_agent(
        prompt=prompt,
        llm=get_local_llm_qwen3(),
        tools=tools,
    )

    grand_agent_executor = AgentExecutor(agent=grand_agent, tools=tools, verbose=True)

    print(grand_agent_executor.invoke({"input": "which season has the most episodes?",}))

    print(grand_agent_executor.invoke({"input":
        "<<<ALWAYS USE THE TOOL>>> Generate in the directory './resources/udemy_qr' in current path, 15 DIFFERENT qrcodes that point to `www.udemy.com/course/langchain`."
        "Verify if the files are created, if not, TRY AGAIN once until it are created. RUN THE CODE and print the results",
    }))
