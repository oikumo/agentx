# Agents - RAG PDF Submodule

## Overview
RAG (Retrieval-Augmented Generation) agent that answers questions about PDF documents using FAISS vector store and Ollama embeddings.

## Key Files

| File | Description |
|------|-------------|
| `agent_rag_pdf.py` | `AgentRagPdf` class - PDF ingestion → FAISS vector store → retrieval QA chain |

## Pipeline
1. Load PDF via `PyPDFLoader`
2. Split into chunks with `CharacterTextSplitter`
3. Create FAISS vector store with Ollama embeddings
4. Answer queries using retrieval chain

## Usage
```python
from agents.rag_pdf.agent_rag_pdf import AgentRagPdf
agent = AgentRagPdf()
agent.run(query="What is this PDF about?")
```
