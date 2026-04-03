# App Modules

## Overview
Extended application modules containing LLM integrations (LangChain, LangGraph), data stores, document loaders, and web ingestion pipelines.

## Structure

```
app_modules/
├── data_stores/
│   └── vector_store_faiss.py      # FAISS vector store creation and persistence
├── document_loaders/
│   └── pdf_loader.py              # PDF loading and text chunking via PyPDFLoader
├── llm/
│   ├── langchain/
│   │   ├── react_agents/          # ReAct agents and router agents
│   │   └── tools/                 # LangChain tool implementations
│   └── langgraph/
│       ├── graph_reflector_chain/     # Generate ↔ reflect loop
│       └── graph_reflexion_agent/     # Draft → execute → revise loop
└── web_ingestion_app/
    ├── documents.py               # Document processing and indexing
    ├── helpers.py                 # JSONL serialization, URL chunking
    ├── tavily.py                  # Tavily extract and map wrappers
    ├── web_ingestion.py           # Entry point script
    └── web_ingestion_app.py       # Full web ingestion pipeline
```

## Key Integrations
- **LangChain**: ReAct agents, tool calling, CSV agents, PythonREPL agents
- **LangGraph**: StateGraph workflows for reflection and reflexion patterns
- **Tavily**: Web search, URL extraction, site mapping
- **FAISS**: Vector store for semantic search/RAG
- **PyPDF**: PDF document loading and chunking
