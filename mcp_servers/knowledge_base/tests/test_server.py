"""End-to-end MCP integration test.

Spawns `server.py` as a subprocess speaking JSON-RPC over stdio, runs the
initialize/initialized/tools-list handshake, and confirms all seven tools
are exposed and `kb_list_categories` returns the documented payload.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_PACKAGE_ROOT = Path(__file__).resolve().parent.parent  # mcp_servers/knowledge_base


def _spawn_server():
    """Run the server module directly in a subprocess.

    We launch it with the current `python` interpreter (the one running
    pytest), inheriting the chromadb install that pytest itself relies on.
    """
    env = os.environ.copy()
    # Make `import kb` work inside the subprocess.
    env["PYTHONPATH"] = str(REPO_PACKAGE_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.Popen(
        [sys.executable, str(REPO_PACKAGE_ROOT / "server.py")],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        cwd=str(REPO_PACKAGE_ROOT),
    )


def _rpc(proc, request):
    proc.stdin.write(json.dumps(request) + "\n")
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())


@pytest.fixture
def mcp_server():
    proc = _spawn_server()
    # initialize handshake
    init = _rpc(proc, {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "0.1"},
        },
    })
    assert "result" in init, f"initialize failed: {init}"
    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    proc.stdin.flush()
    yield proc
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def test_server_exposes_all_seven_tools(mcp_server):
    data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = {t["name"] for t in data["result"]["tools"]}
    expected = {
        "kb_search_tool",
        "kb_ask_tool",
        "kb_add_tool",
        "kb_stats_tool",
        "kb_reset_tool",
        "kb_populate_workspace_tool",
        "kb_list_categories",
    }
    assert expected.issubset(tools), f"missing tools: {expected - tools}"


def test_kb_list_categories_returns_documented_payload(mcp_server):
    data = _rpc(mcp_server, {
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "kb_list_categories", "arguments": {}},
    })
    text = data["result"]["content"][0]["text"]
    assert "Valid Entry Types" in text
    assert "pattern" in text
    assert "Valid Categories" in text
    assert "architecture" in text


def test_kb_add_tool_rejects_invalid_entry_type(mcp_server):
    data = _rpc(mcp_server, {
        "jsonrpc": "2.0", "id": 4, "method": "tools/call",
        "params": {"name": "kb_add_tool", "arguments": {
            "entry_type": "bogus", "category": "class",
            "title": "T", "finding": "f", "solution": "s",
        }},
    })
    text = data["result"]["content"][0]["text"]
    assert "Invalid entry_type" in text


def test_kb_add_tool_rejects_out_of_range_confidence(mcp_server):
    data = _rpc(mcp_server, {
        "jsonrpc": "2.0", "id": 5, "method": "tools/call",
        "params": {"name": "kb_add_tool", "arguments": {
            "entry_type": "pattern", "category": "class",
            "title": "T", "finding": "f", "solution": "s",
            "confidence": 2.0,
        }},
    })
    text = data["result"]["content"][0]["text"]
    assert "Confidence must be between" in text
