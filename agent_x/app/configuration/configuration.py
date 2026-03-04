from dataclasses import dataclass
from pydantic import BaseModel, Field

from agent_x.app.agent_x import AgentX

@dataclass
class LLMModel(BaseModel):
    name: str = Field(description="Name of the model")

class AgentXConfiguration:
    llm_models: list[LLMModel] = []

    def __init__(self):
        self.llm_models = []

def configure_agentx(config: AgentXConfiguration, agentx: AgentX):

    return True
