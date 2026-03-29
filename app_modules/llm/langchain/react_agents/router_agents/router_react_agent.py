from typing import Any

from dotenv import load_dotenv
from langchain_classic import hub
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

from app_modules.llm.langchain.react_agents.router_agents.agent_executors.csv_agent import create_csv_agent_executor
from app_modules.llm.langchain.react_agents.router_agents.agent_executors.qr_react_agent import \
    create_qr_react_agent_executor
from llm_models.local.llama_cpp.llamacpp_config import LlamaCppConfig
from llm_models.local.llama_cpp_factory import model_factory_llamacpp, LLAMA_CPP_MODEL_QWEN_2_5

load_dotenv()


def router_agent():
    print("router_agent start")

    config = LlamaCppConfig()
    config.model_filename = LLAMA_CPP_MODEL_QWEN_2_5
    config.context_size = 32768
    llm = model_factory_llamacpp.create_model_instance(config)

    python_agent_executor = create_qr_react_agent_executor(llm)

    def python_agent_executor_wrapper(original_prompt: str) -> dict[str, Any]:
        return python_agent_executor.invoke({"input": original_prompt})

    csv_agent_executor = create_csv_agent_executor(llm, "resources/episode_info.csv")

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
        llm=llm,
        tools=tools,
    )

    grand_agent_executor = AgentExecutor(agent=grand_agent, tools=tools, verbose=True)

    print(grand_agent_executor.invoke({"input": "which season has the most episodes?"}))

    print(
        grand_agent_executor.invoke(
            {
                "input": "Create a directory the 'udemy_qr' folder, 15 DIFFERENT qrcodes that point to `www.udemy.com/course/langchain"
            }
        )
    )
