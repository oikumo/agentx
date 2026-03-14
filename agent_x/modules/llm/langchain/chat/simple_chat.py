from langchain_core.prompts import PromptTemplate


def simple_chat_prompt_template(llm, query, information):
    print(f"simple_chat {query} {information}")

    summary_template = """responds this query: "{query}"\n  with the given information: {information}"""

    summary_prompt_template = PromptTemplate(
        input_variables=["query", "information"], template=summary_template
    )

    chain = summary_prompt_template | llm
    response = chain.invoke(input={"information": information, "query": query})

    print(response.content)
