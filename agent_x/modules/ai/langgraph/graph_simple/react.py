from dotenv import load_dotenv
from langchain_community.chat_models import ChatLlamaCpp
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from agent_x.app.llm.llms import get_llama_cpp_llm, get_local_llm_qwen3

load_dotenv()

@tool
def triple(num:float) -> float:
    """
    param num: a number to triple
    returns: the triple of the input number
    """
    return float(num) * 3

tools = [TavilySearch(max_results=1), triple]

#llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)
llm = get_local_llm_qwen3().bind_tools(tools)