#!/usr/bin/env python3
"""
MCP Server: Knowledge Base RAG Server for opencode

This MCP server provides tools for opencode to interact with the
Meta Project Harness Knowledge Base using RAG.

Tools:
- kb_search(query, top_k=5, category=None) - Search KB
- kb_ask(question, top_k=3) - Ask question with RAG
- kb_add_entry(type, category, title, finding, solution, context, confidence) - Add entry
- kb_correct(entry_id, reason, new_finding) - Correct entry
- kb_evolve() - Run evolution cycle
- kb_stats() - Get statistics

Usage:
  python knowledge_base_server.py
"""

import sys
import json
from pathlib import Path

# Add parent path for imports
KB_PATH = Path(__file__).parent.parent.parent.parent / ".meta.knowledge_base"
sys.path.insert(0, str(Path(__file__).parent))

try:
    from rag_tool import (
        rag_search,
        rag_ask,
        rag_add_entry,
        rag_correct,
        rag_evolve,
        rag_stats,
    )
except ImportError:
    from .rag_tool import (
        rag_search,
        rag_ask,
        rag_add_entry,
        rag_correct,
        rag_evolve,
        rag_stats,
    )


def main():
    """MCP server main loop."""
    print("MCP Knowledge Base Server starting...")
    print("Available tools: kb_search, kb_ask, kb_add_entry, kb_correct, kb_evolve, kb_stats")
    print("Waiting for requests...\n")
    
    # Read requests from stdin
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            tool_name = request.get("tool")
            params = request.get("params", {})
            
            print(f"Received request: {tool_name}")
            
            # Route to appropriate function
            if tool_name == "kb_search":
                result = rag_search(
                    query=params.get("query", ""),
                    top_k=params.get("top_k", 5),
                    category=params.get("category")
                )
            elif tool_name == "kb_ask":
                result = rag_ask(
                    question=params.get("question", ""),
                    top_k=params.get("top_k", 3)
                )
            elif tool_name == "kb_add_entry":
                result = rag_add_entry(
                    entry_type=params.get("type", "pattern"),
                    category=params.get("category", "workflow"),
                    title=params.get("title", ""),
                    finding=params.get("finding", ""),
                    solution=params.get("solution", ""),
                    context=params.get("context", ""),
                    confidence=params.get("confidence", 0.5)
                )
            elif tool_name == "kb_correct":
                result = rag_correct(
                    entry_id=params.get("entry_id", ""),
                    reason=params.get("reason", ""),
                    new_finding=params.get("new_finding", "")
                )
            elif tool_name == "kb_evolve":
                result = rag_evolve()
            elif tool_name == "kb_stats":
                result = rag_stats()
            else:
                result = {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                    "message": f"Available tools: kb_search, kb_ask, kb_add_entry, kb_correct, kb_evolve, kb_stats"
                }
            
            # Send response
            response = json.dumps(result, indent=2)
            print(f"Response: {response}\n")
            print(json.dumps({"result": result}), flush=True)
            
        except json.JSONDecodeError as e:
            error = {"error": f"Invalid JSON: {str(e)}"}
            print(json.dumps(error), flush=True)
        except Exception as e:
            error = {"error": f"Server error: {str(e)}"}
            print(json.dumps(error), flush=True)


if __name__ == "__main__":
    main()
