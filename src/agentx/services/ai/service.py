from agentx.services.ai.providers import OpenRouterProvider, LlamaCppProvider, OpenAIProvider
from agentx.services.ai.vectorstores.vectorstore_chroma import vectorstore_chroma_ollama


class AIService:
    def openrouter_llm_provider(self) -> OpenRouterProvider:
        return OpenRouterProvider()

    def local_llm_provider(self, model_filename: str,
            context_size: int) -> LlamaCppProvider:
        return LlamaCppProvider(
            model_filename=model_filename,
            context_size=context_size)

    def cloud_llm_provider(self) -> OpenAIProvider:
        return OpenAIProvider()

    def rag_chromadb(self, directory: str):
        return vectorstore_chroma_ollama(directory)
