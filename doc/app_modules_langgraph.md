# App Modules - LangGraph - Agent-X

**Path**: `/app_modules/llm/langgraph/`

LangGraph workflows: reflection chains and reflexion agents.

---

## Module Structure

```
app_modules/llm/langgraph/
├── graph_reflector_chain/
│   ├── chains.py          # generate/reflect chains
│   └── graph_chains.py    # StateGraph
└── graph_reflexion_agent/
    ├── chains.py          # first_responder, revisor
    ├── graph_reflexion_agent.py
    ├── schemas.py         # Pydantic models
    └── tool_executor.py   # TavilySearch execution
```

---

## Graph Reflector Chain

### graph_reflector_chain/chains.py

**Variables**:
- `reflection_prompt` - ChatPromptTemplate for critiquing tweets (viral twitter influencer persona)
- `generation_prompt` - ChatPromptTemplate for generating tweets (twitter techie influencer persona)
- `llm = ChatOpenAI()` - default OpenAI LLM
- `generate_chain = generation_prompt | llm`
- `reflect_chain = reflection_prompt | llm`

### graph_reflector_chain/graph_chains.py

**Function**: `graph_chains()`

Builds `StateGraph` with generate ↔ reflect loop for tweet improvement.

**Flow**:
1. Defines `MessageGraph` TypedDict with `messages: Annotated[list[BaseMessage], add_messages]`
2. Creates `generation_node` and `reflection_node`
3. Sets up graph: ENTRY → generate → should_continue?
   - If messages > 6 → END
   - Otherwise → reflect → generate (loop)
4. Invokes with a tweet about LangChainAI tool calling
5. Saves output to `local/output.txt`

---

## Graph Reflexion Agent

### graph_reflexion_agent/schemas.py

**Pydantic Models**:
- `Reflection(BaseModel)` - `missing: str`, `superfluous: str` critique fields
- `AnswerQuestion(BaseModel)` - `answer: str`, `reflection: Reflection`, `search_queries: List[str]`
- `ReviseAnswer(AnswerQuestion)` - extends with `references: List[str]`

### graph_reflexion_agent/chains.py

**Variables**:
- `llm = ChatOpenAI(model="o4-mini")`
- `first_responder` - prompt + LLM bound to `AnswerQuestion` tool
- `revisor` - prompt + LLM bound to `ReviseAnswer` tool with revision instructions

**Prompts**:
- `actor_prompt_template` - expert researcher persona with time injection
- `first_responder_prompt_template` - "Provide a detailed ~250 word answer"
- `revise_instructions` - instructions for revision with citations and word limits

### graph_reflexion_agent/tool_executor.py

**Function**: `run_queries(search_queries: list[str], **kwargs)` - batches TavilySearch queries

**Variable**: `execute_tools = ToolNode([...])` - tool node wrapping `run_queries` for `AnswerQuestion` and `ReviseAnswer`

### graph_reflexion_agent/graph_reflexion_agent.py

**Function**: `graph_reflexion_agent()`

Complete reflexion workflow: draft → execute_tools → revise → loop.

**Flow**:
1. `draft_node` - generates initial response via `first_responder`
2. `execute_tools` - runs TavilySearch via `execute_tools` ToolNode
3. `revise_node` - revises answer via `revisor`
4. `event_loop` - checks iteration count (max 2), decides whether to continue or END
5. Graph: START → draft → execute_tools → revise → event_loop?
   - If iterations <= MAX → execute_tools (loop)
   - Otherwise → END
6. Invokes with query about AI-Powered SOC startups
7. Extracts and prints final answer, saves to `local/output.txt`
