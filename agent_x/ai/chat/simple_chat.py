from langchain_core.prompts import PromptTemplate

def simple_chat_prompt_template(llm):
    print("simple_chat")

    information = "game of the year 2025"
    summary_template = '''make a story with the given information {information}'''

    summary_prompt_template = PromptTemplate(
        input_variables=["information"], template=summary_template
    )

    chain = summary_prompt_template | llm
    response = chain.invoke(input= {"information": information})

    print(response.content)