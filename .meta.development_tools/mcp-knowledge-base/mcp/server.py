#!/usr/bin/env python3
"""
MCP Server for Knowledge Base RAG.
Usage: python -m mcp.server or python server.py
"""

import sys
import json
from pathlib import Path

# Ensure parent path is in sys.path
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT_DIR))

# Import from same directory
from mcp import (
    rag_search, rag_ask, rag_add_entry,
    rag_correct, rag_evolve, rag_stats
)


def handle_request(request: dict) -> dict:
    """Handle MCP request."""
    tool_name = request.get("tool")
    params = request.get("params", {})
    
    handlers = {
        "kb_search": lambda: rag_search(params.get("query", ""), params.get("top_k", 5), params.get("category")),
        "kb_ask": lambda: rag_ask(params.get("question", ""), params.get("top_k", 3)),
        "kb_add_entry": lambda: rag_add_entry(
            params.get("type", "pattern"), params.get("category", "workflow"),
            params.get("title", ""), params.get("finding", ""),
            params.get("solution", ""), params.get("context", ""),
            params.get("confidence", 0.5)
        ),
        "kb_correct": lambda: rag_correct(params.get("entry_id", ""), params.get("reason", ""), params.get("new_finding", "")),
        "kb_evolve": rag_evolve,
        "kb_stats": rag_stats,
    }
    
    handler = handlers.get(tool_name)
    if not handler:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}
    
    return handler()


def main():
    """MCP server main loop."""
    print("MCP Knowledge Base Server starting...")
    print("Available tools: kb_search, kb_ask, kb_add_entry, kb_correct, kb_evolve, kb_stats\n")
    
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            result = handle_request(request)
            print(json.dumps({"result": result}, indent=2), flush=True)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {str(e)}"}), flush=True)
        except Exception as e:
            print(json.dumps({"error": f"Server error: {str(e)}"}), flush=True)


if __name__ == "__main__":
    main()
