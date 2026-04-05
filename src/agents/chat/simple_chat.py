from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate


class SimpleChat:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def run(self, query: str, information: str = ""):
        print(f"simple_chat {query} {information}")

        summary_template = """responds this query: "{query}"""

        summary_prompt_template = PromptTemplate(
            input_variables=["query"], template=summary_template
        )

        chain = summary_prompt_template | self.llm
        response = chain.invoke(input={"information": information, "query": query})

        print(response.content)

    def run_streaming(self, query: str, information: str = "") -> str:
        summary_template = """responds this query: "{query}"""

        summary_prompt_template = PromptTemplate(
            input_variables=["query"], template=summary_template
        )

        chain = summary_prompt_template | self.llm
        full_response = ""
        for chunk in chain.stream(input={"information": information, "query": query}):
            content = self._extract_chunk_content(chunk)
            if content:
                full_response += content
        return full_response

    def _extract_chunk_content(self, chunk) -> str:
        if hasattr(chunk, "text"):
            return str(chunk.text)
        if chunk.content is None:
            return ""
        if isinstance(chunk.content, list):
            return " ".join(str(item) for item in chunk.content if item is not None)
        return str(chunk.content)
