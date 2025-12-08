from langchain_core.language_models import BaseLanguageModel

from langchain_classic.agents import AgentExecutor
from langchain_classic.agents.react.agent import create_react_agent
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_tavily import TavilySearch

from typing import List
from pydantic import BaseModel, Field

from agent_x.ai.react_search_agent.prompt import REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS


class Source(BaseModel):
    """Schema for a source used by the agent"""

    url: str = Field(description="The URL of the source")


class AgentResponse(BaseModel):
    """Schema for agent response with answer and sources"""

    answer: str = Field(description="The agent's answer to the query")
    sources: List[Source] = Field(
        default_factory=list, description="List of sources used to generate the answer"
    )

def search_agent(llm: BaseLanguageModel):
    print("search_agent")
    tools = [TavilySearch()]

    # prompt = hub.pull("hwchase17/react") # Prompt template
    # prompt = REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS

    output_parser = PydanticOutputParser(pydantic_object=AgentResponse)
    react_prompt_with_format_instructions = PromptTemplate(
        template=REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS,
        input_variables=["input", "agent_scratchpad", "tool_names"],
    ).partial(format_instructions=output_parser.get_format_instructions())

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=react_prompt_with_format_instructions
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    extract_output = RunnableLambda(lambda x: x["output"])
    parse_output = RunnableLambda(lambda x: output_parser.parse(x))
    chain = agent_executor | extract_output | parse_output

    result = chain.invoke(
        input= {
            "input":"top news today important in Chile"
        }
    )
    print(result)

