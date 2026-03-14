from langchain_openai import ChatOpenAI


def get_remote_llm_openai_gpt4():
    return ChatOpenAI(temperature=0, model="gpt-4-turbo")


def get_remote_llm_openai_gpt3_5_turbo():
    return ChatOpenAI(model="gpt-3.5-turbo")
