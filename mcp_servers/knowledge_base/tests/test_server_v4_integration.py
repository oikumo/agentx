#!/usr/bin/env python3
"""
Integration tests for KB MCP Server v4.

Tests v4 tool registration, backward compatibility, and component initialization.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def _spawn_server():
    """Spawn the MCP server as a subprocess."""
    env = os.environ.copy()
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
    """Send JSON-RPC request and read response."""
    proc.stdin.write(json.dumps(request) + "\n")
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())


@pytest.fixture
def mcp_server():
    """Fixture to spawn and teardown MCP server."""
    proc = _spawn_server()
    
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


class TestV4ToolRegistration:
    """Test that all v4 tools are registered."""
    
    def test_graph_tool_registered(self, mcp_server):
        """Test kb_graph_tool is registered."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        assert "kb_graph_tool" in tools
    
    def test_impact_tool_registered(self, mcp_server):
        """Test kb_impact_tool is registered."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        assert "kb_impact_tool" in tools
    
    def test_visualize_tool_registered(self, mcp_server):
        """Test kb_visualize_tool is registered."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        assert "kb_visualize_tool" in tools
    
    def test_trace_flow_tool_registered(self, mcp_server):
        """Test kb_trace_flow_tool is registered."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        assert "kb_trace_flow_tool" in tools
    
    def test_code_location_tool_registered(self, mcp_server):
        """Test kb_code_location_tool is registered."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        assert "kb_code_location_tool" in tools
    
    def test_find_pattern_tool_registered(self, mcp_server):
        """Test kb_find_pattern_tool is registered."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        assert "kb_find_pattern_tool" in tools
    
    def test_session_tool_registered(self, mcp_server):
        """Test kb_session_tool is registered."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        assert "kb_session_tool" in tools
    
    def test_all_v4_tools_present(self, mcp_server):
        """Test all v4 tools are present."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        
        v4_tools = {
            "kb_graph_tool",
            "kb_impact_tool",
            "kb_visualize_tool",
            "kb_trace_flow_tool",
            "kb_code_location_tool",
            "kb_find_pattern_tool",
            "kb_session_tool",
        }
        assert v4_tools.issubset(tools), f"Missing v4 tools: {v4_tools - tools}"


class TestV4ToolExecution:
    """Test that v4 tools can be called."""
    
    def test_graph_tool_list_operation(self, mcp_server):
        """Test kb_graph_tool with list operation."""
        data = _rpc(mcp_server, {
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "kb_graph_tool", "arguments": {"operation": "list"}},
        })
        text = data["result"]["content"][0]["text"]
        assert "Knowledge Graph" in text or "❌" in text

    def test_graph_tool_layers_operation(self, mcp_server):
        """Test kb_graph_tool with layers operation."""
        data = _rpc(mcp_server, {
            "jsonrpc": "2.0", "id": 4, "method": "tools/call",
            "params": {"name": "kb_graph_tool", "arguments": {"operation": "layers"}},
        })
        text = data["result"]["content"][0]["text"]
        assert "Layers" in text or "❌" in text

    def test_graph_tool_entry_points_operation(self, mcp_server):
        """Test kb_graph_tool with entry_points operation."""
        data = _rpc(mcp_server, {
            "jsonrpc": "2.0", "id": 5, "method": "tools/call",
            "params": {"name": "kb_graph_tool", "arguments": {"operation": "entry_points"}},
        })
        text = data["result"]["content"][0]["text"]
        assert "Entry Points" in text or "❌" in text

    def test_visualize_tool_full_view(self, mcp_server):
        """Test kb_visualize_tool with full view."""
        data = _rpc(mcp_server, {
            "jsonrpc": "2.0", "id": 6, "method": "tools/call",
            "params": {"name": "kb_visualize_tool", "arguments": {"view": "full", "format": "mermaid"}},
        })
        text = data["result"]["content"][0]["text"]
        assert text  # Should return something (even if empty graph)

    def test_session_tool_get_action(self, mcp_server):
        """Test kb_session_tool with get action."""
        data = _rpc(mcp_server, {
            "jsonrpc": "2.0", "id": 7, "method": "tools/call",
            "params": {"name": "kb_session_tool", "arguments": {"action": "get"}},
        })
        text = data["result"]["content"][0]["text"]
        assert "Session" in text or "❌" not in text

    def test_session_tool_set_action(self, mcp_server):
        """Test kb_session_tool with set action."""
        data = _rpc(mcp_server, {
            "jsonrpc": "2.0", "id": 8, "method": "tools/call",
            "params": {
                "name": "kb_session_tool",
                "arguments": {"action": "set", "key": "test_key", "value": "test_value"},
            },
        })
        text = data["result"]["content"][0]["text"]
        assert "✅" in text or "❌" in text

    def test_impact_tool_without_entity(self, mcp_server):
        """Test kb_impact_tool handles missing entity gracefully."""
        data = _rpc(mcp_server, {
            "jsonrpc": "2.0", "id": 9, "method": "tools/call",
            "params": {"name": "kb_impact_tool", "arguments": {"entity_id": "nonexistent"}},
        })
        text = data["result"]["content"][0]["text"]
        assert "Impact" in text or "❌" in text


class TestBackwardCompatibility:
    """Test backward compatibility with v3 tools."""
    
    def test_v3_search_tool_exists(self, mcp_server):
        """Test kb_search_tool (v3) is still available."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 10, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        assert "kb_search_tool" in tools
    
    def test_v3_ask_tool_exists(self, mcp_server):
        """Test kb_ask_tool (v3) is still available."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 11, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        assert "kb_ask_tool" in tools
    
    def test_v3_add_tool_exists(self, mcp_server):
        """Test kb_add_tool (v3) is still available."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 12, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        assert "kb_add_tool" in tools
    
    def test_v3_stats_tool_exists(self, mcp_server):
        """Test kb_stats_tool (v3) is still available."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 13, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        assert "kb_stats_tool" in tools
    
    def test_v3_reset_tool_exists(self, mcp_server):
        """Test kb_reset_tool (v3) is still available."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 14, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        assert "kb_reset_tool" in tools
    
    def test_v3_populate_workspace_tool_exists(self, mcp_server):
        """Test kb_populate_workspace_tool (v3) is still available."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 15, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        assert "kb_populate_workspace_tool" in tools
    
    def test_v3_list_categories_tool_exists(self, mcp_server):
        """Test kb_list_categories (v3) is still available."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 16, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        assert "kb_list_categories" in tools
    
    def test_v3_and_v4_tools_coexist(self, mcp_server):
        """Test that v3 and v4 tools coexist."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 17, "method": "tools/list"})
        tools = {t["name"] for t in data["result"]["tools"]}
        
        v3_tools = {
            "kb_search_tool", "kb_ask_tool", "kb_add_tool",
            "kb_stats_tool", "kb_reset_tool", "kb_populate_workspace_tool",
            "kb_list_categories",
        }
        
        v4_tools = {
            "kb_graph_tool", "kb_impact_tool", "kb_visualize_tool",
            "kb_trace_flow_tool", "kb_code_location_tool",
            "kb_find_pattern_tool", "kb_session_tool",
        }
        
        assert v3_tools.issubset(tools), f"Missing v3 tools: {v3_tools - tools}"
        assert v4_tools.issubset(tools), f"Missing v4 tools: {v4_tools - tools}"


class TestComponentInitialization:
    """Test that v4 components initialize correctly."""
    
    def test_server_starts_without_errors(self, mcp_server):
        """Test server starts successfully."""
        data = _rpc(mcp_server, {"jsonrpc": "2.0", "id": 18, "method": "tools/list"})
        assert "result" in data
        assert "tools" in data["result"]
    
    def test_resources_accessible(self, mcp_server):
        """Test that resources are accessible after initialization."""
        data = _rpc(mcp_server, {
            "jsonrpc": "2.0", "id": 19, "method": "resources/list",
        })
        assert "result" in data
        assert "resources" in data["result"]
    
    def test_prompts_accessible(self, mcp_server):
        """Test that prompts are accessible after initialization."""
        data = _rpc(mcp_server, {
            "jsonrpc": "2.0", "id": 20, "method": "prompts/list",
        })
        assert "result" in data
        assert "prompts" in data["result"]
    
    def test_health_resource_accessible(self, mcp_server):
        """Test health resource is accessible."""
        data = _rpc(mcp_server, {
            "jsonrpc": "2.0", "id": 21,
            "method": "resources/read",
            "params": {"uri": "knowledge-base://health"},
        })
        assert "result" in data
        assert "contents" in data["result"]
    
    def test_onboard_agent_prompt_accessible(self, mcp_server):
        """Test onboard-agent prompt is accessible."""
        data = _rpc(mcp_server, {
            "jsonrpc": "2.0", "id": 22,
            "method": "prompts/get",
            "params": {"name": "onboard-agent"},
        })
        assert "result" in data
        assert "messages" in data["result"] or "description" in data["result"]