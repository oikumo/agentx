from langchain_classic.agents import AgentExecutor
from langchain_core.language_models import BaseLanguageModel
from langchain_experimental.agents.agent_toolkits import create_csv_agent


def create_csv_agent_executor(llm: BaseLanguageModel, file_path: str):
    print("create_csv_agent_executor")

    csv_agent_executor: AgentExecutor = create_csv_agent(
        llm=llm, path=file_path, verbose=True, allow_dangerous_code=True
    )

    return csv_agent_executor
