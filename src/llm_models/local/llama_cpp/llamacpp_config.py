from pydantic import BaseModel


class LlamaCppConfig(BaseModel):
    model_filename: str = ""
    temperature: int = 0.7
    context_size: int = 4096
    max_tokens: int = 512
    top_p: int = 0.5
    batch_size: int = 64
