from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

def get_local_llm_qwen2_5():
    return ChatOllama(temperature=0, model="qwen2.5:1.5b", reasoning=False)

def get_local_llm_qwen2_5_coder():
    return ChatOllama(temperature=0, model="qwen2.5-coder:1.5b", reasoning=False)

def get_local_llm_qwen3():
    return ChatOllama(temperature=0, model="qwen3:1.7b", reasoning=True)

def get_remote_llm_openai_gpt4():
    return ChatOpenAI(temperature=0, model="gpt-4-turbo")

def get_remote_llm_openai_gpt3_5_turbo():
    return ChatOpenAI(model= 'gpt-3.5-turbo')