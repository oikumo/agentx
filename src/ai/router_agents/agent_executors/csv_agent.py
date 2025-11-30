from langchain_classic.agents import AgentExecutor
from langchain_experimental.agents.agent_toolkits import create_csv_agent

from ai.llm.llms import get_local_llm_gemma3, get_llama_cpp_llm


def create_csv_agent_executor(file_path:str):
    print("create_csv_agent_executor")
    llm = get_local_llm_gemma3()

    csv_agent_executor: AgentExecutor = create_csv_agent(
        llm=llm,
        path=file_path,
        verbose=True,
        allow_dangerous_code=True
    )

    return csv_agent_executor