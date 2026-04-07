from llm_models.local.ollama.ollama import Ollama

LOCAL_OLLAMA_MODEL_QWEN_3_5 = "qwen3.5:0.8b"

class LocalOllamaModelManager:
    def get_think_model(self):
        return Ollama(LOCAL_OLLAMA_MODEL_QWEN_3_5).get_model()


local_ollama_models = LocalOllamaModelManager()