from langchain_core.language_models import BaseChatModel

from agents.react_web_search.search_agent import search_agent


class AgentReactWebSearch:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def run(self):
        search_agent(llm=self.llm)

    def run_streaming(self, query: str) -> str:
        from typing import List

        from langchain_classic.agents import AgentExecutor
        from langchain_classic.agents.react.agent import create_react_agent
        from langchain_core.output_parsers.pydantic import PydanticOutputParser
        from langchain_core.prompts import PromptTemplate
        from langchain_core.runnables import RunnableLambda
        from langchain_tavily import TavilySearch
        from pydantic import BaseModel, Field

        from agents.react_web_search.prompt import REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS

        class Source(BaseModel):
            url: str = Field(description="The URL of the source")

        class AgentResponse(BaseModel):
            answer: str = Field(description="The agent's answer to the query")
            sources: List[Source] = Field(
                default_factory=list, description="List of sources"
            )

        tools = [TavilySearch()]
        output_parser = PydanticOutputParser(pydantic_object=AgentResponse)
        react_prompt = PromptTemplate(
            template=REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS,
            input_variables=["input", "agent_scratchpad", "tool_names"],
        ).partial(format_instructions=output_parser.get_format_instructions())

        agent = create_react_agent(llm=self.llm, tools=tools, prompt=react_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        extract_output = RunnableLambda(lambda x: x["output"])

        chain = agent_executor | extract_output
        result = chain.invoke(input={"input": query})
        return str(result)
