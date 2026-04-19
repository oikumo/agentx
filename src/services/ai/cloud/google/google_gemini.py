from langchain_google_genai import ChatGoogleGenerativeAI

def get_remote_llm_google_gemini():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=1.0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )