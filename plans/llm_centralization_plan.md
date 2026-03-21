# Planto Centralize LLM Configuration in Agent-X

## Current State Analysis
The Agent-X codebase has LLM configurations scattered across multiple files:
- `agent_x/llm_models/local/llms.py` - Local models (Ollama, llama.cpp)
- `agent_x/llm_models/cloud/llms.py` - Cloud models (OpenAI)
- `agent_x/applications/repl_app/commands/llm_chat_commands.py` - Command usage
- `agent_x/modules/llm/langgraph/` - Graph implementations
- `agent_x/modules/llm/functions/function_call.py` - Specialized function model

While an `AgentXConfiguration` class exists in `agent_x/app/configuration/configuration.py`, it's underutilized for LLM management.

## Proposed Solution

### Phase 1: Enhance Configuration System
1. **Extend `AgentXConfiguration`** with:
   - `LLMConfig` model for specific LLM instances
   - Default configurations for chat/embedding models
   - Environment-based loading
   - Validation for required credentials

2. **Create Central LLM Factory**:
   - New module: `agent_x/llm_factory.py`
   - Centralized model instantiation with caching
   - Provider-specific creation methods
   - Fallback mechanisms

### Phase 2: Centralize Configuration
Define standard configurations:
- Chat: `qwen3:1.7b` (default), `gpt-4-turbo`, `qwen2.5:1.5b`
- Embedding: `nomic-embed-text` (default), `text-embedding-3-small`
- Specialized: `functiongemma:270m-it-fp16` for function calls

### Phase 3: Update Usage Points
Replace scattered implementations:
- Update `llm_chat_commands.py` commands
- Update langgraph modules
- Update function call module
- Maintain backward compatibility

### Implementation Highlights

**Enhanced Configuration** (`configuration.py`):
```python
class LLMConfig(BaseModel):
    name: str
    provider: LLMProvider
    model_name: str  # Actual identifier like "gpt-4-turbo"
    temperature: float = 0.7
    max_tokens: int = 2048
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    extra_params: Dict[str, Any] = {}

class AgentXConfiguration(BaseModel):
    llm_configs: List[LLMConfig] = Field(default_factory=list)
    default_chat_model: str = "qwen3:1.7b"
    default_embedding_model: str = "nomic-embed-text"
    
    def get_llm_config(self, name: str) -> Optional[LLMConfig]:
        # Return config by name
```

**LLM Factory** (`llm_factory.py`):
```python
class LLMFactory:
    def __init__(self, config: AgentXConfiguration):
        self.config = config
        self._cache = {}
    
    def get_chat_model(self, name: Optional[str] = None) -> BaseLanguageModel:
        model_name = name or self.config.default_chat_model
        # Check cache, get config, create model, cache and return
    
    def _create_ollama_model(self, config: LLMConfig) -> ChatOllama:
        return ChatOllama(
            model=config.model_name,
            temperature=config.temperature,
            # ... other params from config
        )
    
    def _create_openai_model(self, config: LLMConfig) -> ChatOpenAI:
        return ChatOpenAI(
            model=config.model_name,
            temperature=config.temperature,
            api_key=config.api_key,
            # ... other params
        )
```

**Usage Example** (replacing scattered calls):
```python
# Before: from agent_x.llm_models.local.llms import get_local_llm_qwen3
#         llm = get_local_llm_qwen3()

# After: from agent_x.llm_factory import LLMFactory
#        llm = factory.get_chat_model("qwen3:1.7b")
```

### Benefits
1. **Single Source of Truth**: All LLM configs in one place
2. **Environment Flexibility**: Easy dev/staging/prod switching
3. **Better Testing**: Mock-friendly for unit tests
4. **Validation**: Pydantic ensures valid configurations
5. **Performance**: Caching prevents redundant creation
6. **Maintainability**: Clear separation of concerns

### Migration Approach
1. Create enhanced config and factory (backward compatible)
2. Update subsystems incrementally (start with chat commands)
3. Migrate remaining components
4. Remove old scattered configurations
5. Add advanced features (hot-reloading, metrics)