from langchain_core.language_models import BaseChatModel

from agents.react_web_search.search_agent import search_agent


class AgentReactWebSearch:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def run(self):
        search_agent(llm=self.llm)