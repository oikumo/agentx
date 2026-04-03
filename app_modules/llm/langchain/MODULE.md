# App Modules - LLM / LangChain

## Overview
LangChain-based agent implementations including ReAct agents, router agents, and tool integrations.

## Structure

```
llm/langchain/
├── react_agents/
│   ├── react_agents_tools/
│   │   ├── callbacks.py           # AgentCallbackHandler - prints prompts/responses
│   │   └── react_tools.py         # ReAct agent with tools (get_text_length, etc.)
│   └── router_agents/
│       ├── router_react_agent.py  # Grand agent routing between Python + CSV agents
│       └── agent_executors/
│           ├── csv_agent.py       # CSV/pandas querying via create_csv_agent
│           └── qr_react_agent.py  # QR code generation via PythonREPLTool
└── tools/
    ├── simple_tool.py             # multiply tool with create_tool_calling_agent
    └── tavily_web_search/
        └── simple_tool_search_tavily.py  # Tavily search + multiply tool agent
```

## Key Features
- **ReAct Pattern**: Thought → Action → Observation loop with intermediate step tracking
- **Tool Calling**: `@tool` decorator, `PythonREPLTool`, `TavilySearchResults`
- **Router Agent**: Routes between specialized sub-agents (Python, CSV)
- **CSV Agent**: Pandas-based CSV querying
- **QR Agent**: Python code execution for QR code generation
