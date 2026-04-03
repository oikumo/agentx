# App Modules - LangChain - Agent-X

**Path**: `/app_modules/llm/langchain/`

LangChain integrations: ReAct agents, router agents, tools.

---

## Module Structure

```
app_modules/llm/langchain/
├── tools/
│   ├── simple_tool.py         # multiply tool
│   └── tavily_web_search/
│       └── simple_tool_search_tavily.py
└── react_agents/
    ├── react_agents_tools/
    │   ├── callbacks.py       # AgentCallbackHandler
    │   └── react_tools.py     # manual ReAct loop
    └── router_agents/
        ├── router_react_agent.py
        └── agent_executors/
            ├── csv_agent.py
            └── qr_react_agent.py
```

---

## Tools

### tools/simple_tool.py

**Function**: `@tool multiply(x: float, y: float) -> float`

Standalone multiply tool definition.

**Function**: `simple_tool(llm: BaseLanguageModel)` - creates tool-calling agent with multiply tool, invokes with test prompt.

### tools/tavily_web_search/simple_tool_search_tavily.py

**Function**: `@tool multiply(x: float, y: float) -> float`

**Function**: `simple_tool_search_tavily(llm: BaseLanguageModel)` - creates tool-calling agent with `TavilySearchResults` + `multiply` tools, invokes with weather comparison query.

---

## ReAct Agents

### react_agents/react_agents_tools/callbacks.py

**Class**: `AgentCallbackHandler(BaseCallbackHandler)`

Callback handler that prints prompts and LLM responses during agent execution.

**Methods**:
- `on_llm_start(...)` - prints prompts
- `on_llm_end(response: LLMResult, ...)` - prints LLM response text

### react_agents/react_agents_tools/react_tools.py

**Function**: `@tool get_text_length(text: str) -> int` - returns character count

**Function**: `find_tool_by_name(tools: List[Tool], tool_name: str) -> Tool` - lookup helper

**Function**: `react_tools(llm: BaseLanguageModel)` - manual ReAct loop implementation:
1. Sets up prompt with tool descriptions
2. Configures LLM stop tokens and callbacks
3. Builds agent chain: `{"input", "agent_scratchpad"} | prompt | llm | ReActSingleInputOutputParser`
4. Runs manual loop: invoke agent → if `AgentAction`, execute tool → append to intermediate steps → repeat until `AgentFinish`
5. Prints final return values

---

## Router Agents

### router_agents/router_react_agent.py

**Function**: `router_agent()`

Creates a router agent that dispatches between:
- **Python Agent**: QR code generation via `PythonREPLTool`
- **CSV Agent**: Pandas-based CSV querying of `episode_info.csv`

**Flow**:
1. Creates LlamaCpp Qwen 2.5 LLM
2. Wraps `create_qr_react_agent_executor` and `create_csv_agent_executor` as `Tool` instances
3. Creates ReAct agent with both tools
4. Invokes with two test queries:
   - "which season has the most episodes?"
   - "Create a directory the 'udemy_qr' folder, 15 DIFFERENT qrcodes..."

### router_agents/agent_executors/csv_agent.py

**Function**: `create_csv_agent_executor(llm: BaseLanguageModel, file_path: str) -> AgentExecutor`

Creates CSV agent using `create_csv_agent` from `langchain_experimental`. Uses `allow_dangerous_code=True` for pandas execution.

### router_agents/agent_executors/qr_react_agent.py

**Function**: `create_qr_react_agent_executor(llm: BaseLanguageModel)`

Creates ReAct agent with `PythonREPLTool` for QR code generation. Instructions tell the agent to write and execute Python code, handle errors, and use the `qrcode` package.
