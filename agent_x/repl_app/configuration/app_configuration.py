from typing import List

from pydantic import BaseModel, Field

class LLMModel(BaseModel):
    name: str = Field(description="Name of the model")

class AppConfiguration(BaseModel):
    description: str = ""
    llmModels: list[LLMModel] = []


