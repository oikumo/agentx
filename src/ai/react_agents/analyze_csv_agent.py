from langchain_classic import hub
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain_experimental.agents.agent_toolkits import create_csv_agent

from ai.llm.llms import get_local_llm_gemma3, get_llama_cpp_llm


def analyze_csv(file_path:str):
    print("analyze_csv")
    base_prompt = hub.pull("langchain-ai/react-agent-template")
    prompt = base_prompt.partial(instructions="")
    llm = get_local_llm_gemma3()

    csv_agent_executor: AgentExecutor = create_csv_agent(
        llm=llm,
        path=file_path,
        verbose=True,
        allow_dangerous_code=True
    )

    tools = [
        Tool(
            name="CSV Agent",
            func=csv_agent_executor.invoke,
            description="""useful when you need to answer question over episode_info.csv file,
                         takes an input the entire question and returns the answer after running pandas calculations""",
        ),
    ]

    grand_agent = create_react_agent(
        prompt=prompt,
        llm= llm,
        tools=tools,
    )

    grand_agent_executor = AgentExecutor(agent=grand_agent, tools=tools, verbose=True)

    print(
        grand_agent_executor.invoke(
            {
                "input": "which season has the most episodes?",
            }
        )
    )