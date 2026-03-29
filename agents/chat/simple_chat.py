from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate

class SimpleChat:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def run(self, query: str, information: str = ""):
        print(f"simple_chat {query} {information}")

        #summary_template = """responds this query: "{query}"\n  with the given information: {information}"""
        summary_template = """responds this query: "{query}"""

        summary_prompt_template = PromptTemplate(
            #input_variables=["query", "information"], template=summary_template
            input_variables=["query"], template=summary_template
        )

        chain = summary_prompt_template | self.llm
        response = chain.invoke(input={"information": information, "query": query})

        print(response.content)
