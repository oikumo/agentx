from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_community.chat_models import ChatLlamaCpp
import multiprocessing

def get_llama_cpp_llm() :
    model_path = "/home/oikumo/.cache/llama.cpp/unsloth_Qwen3-1.7B-GGUF_Qwen3-1.7B-Q4_K_M.gguf"
    model_path = "/home/oikumo/.cache/llama.cpp/ggml-org_gemma-3-1b-it-GGUF_gemma-3-1b-it-Q4_K_M.gguf"
    return ChatLlamaCpp(
            temperature=0,
            model_path=model_path,
            n_ctx=32768,
            max_tokens=512,
            n_threads=multiprocessing.cpu_count() - 1,
            repeat_penalty=1.5,
            top_p=0.5,
            verbose=False)

def get_local_llm_qwen3():
    # llm=ChatOpenAI(temperature=0, model="gpt-4-turbo"),
    return ChatOllama(temperature=0, model="qwen3:1.7b", reasoning=True)
    # llm = ChatOllama(temperature=0, model="gemma3n:e2b"),

def get_local_llm_gemma3():
    return ChatOllama(temperature=0, model="qwen3:1.7b", reasoning=True)
    #return ChatOllama(temperature=0, model="gemma3:1b"),