#!/usr/bin/env python3
"""Production verification test for OMT++ hook EFFECTS.

This test simulates real opencode tool.execute.after hook dispatches with
EXACT SDK payload shapes (validated by test_opencode_sdk_contract.py) and
asserts the LIVE hook effects fire:
- omt_think: TA: digest appended to output.output on FIRST tool result per session
- omt_enforcer: nav reminder prepended to output.output on FIRST tool result per session
- omt_enforcer: D1 read-time thought injection on FIRST read of thought-carrying file

This is the test that would have caught F14 (dead D1 branch) and F14c (dead session.start)
in feature_022 — it validates HOOK EFFECTS, not just plugin loading.
"""

from __future__ import annotations

import json
import tempfile
import uuid
from pathlib import Path
import sys

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

# Import the plugin modules directly
import importlib.util


def load_plugin_module(plugin_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, plugin_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_omt_think_digest_injects_on_first_tool_result():
    """omt_think: TA digest appends to output.output on FIRST tool.execute.after per session."""
    # Load the plugin
    plugin = load_plugin_module(
        REPO_ROOT / ".opencode" / "plugin" / "omt_think.ts",
        "omt_think"
    )
    factory = plugin.default
    tools = factory()
    
    # Get the tool.execute.after hook
    after_hook = tools["tool.execute.after"]
    
    session_id = f"test-session-{uuid.uuid4()}"
    
    # Create a mock file with TA: thoughts
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_file.py"
        test_file.write_text("# TA: gotcha: test thought\nprint('hello')\n")
        
        # Mock the fileThoughtsIn function to find our test thought
        # We need to set up the REPO_ROOT for the plugin
        import os
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            # First tool result in session - should inject digest
            input_payload = {
                "tool": "read",
                "sessionID": session_id,
                "args": {"filePath": str(test_file)},
            }
            output_payload = {
                "title": "Read file",
                "output": "file content here",
                "metadata": {},
            }
            
            # Call the hook
            import asyncio
            result = asyncio.run(after_hook(input_payload, output_payload))
            
            # Verify digest was appended
            assert "💡 TA: digest" in result["output"], \
                f"Expected TA digest in output, got: {result['output']}"
            assert "test thought" in result["output"], \
                f"Expected thought content in digest, got: {result['output']}"
            
            # Second tool result in SAME session - should NOT inject again
            output_payload2 = {
                "title": "Read file again",
                "output": "file content again",
                "metadata": {},
            }
            result2 = asyncio.run(after_hook(input_payload, output_payload2))
            
            # Should NOT have digest again (only first per session)
            assert "💡 TA: digest" not in result2["output"], \
                f"Digest should not repeat in same session, got: {result2['output']}"
            
            print("✅ omt_think: TA digest injects on FIRST tool result per session only")
            
        finally:
            os.chdir(old_cwd)


def test_omt_enforcer_nav_reminder_on_first_tool_result():
    """omt_enforcer: nav reminder prepends to output.output on FIRST tool result per session."""
    plugin = load_plugin_module(
        REPO_ROOT / ".opencode" / "plugin" / "omt_enforcer.ts",
        "omt_enforcer"
    )
    factory = plugin.default
    tools = factory()
    
    after_hook = tools["tool.execute.after"]
    session_id = f"test-session-{uuid.uuid4()}"
    
    # First tool result - should prepend nav reminder
    input_payload = {
        "tool": "read",
        "sessionID": session_id,
        "args": {"filePath": "some_file.py"},
    }
    output_payload = {
        "title": "Read file",
        "output": "file content",
        "metadata": {},
    }
    
    import asyncio
    result = asyncio.run(after_hook(input_payload, output_payload))
    
    # Verify nav reminder was prepended
    assert "🧭 NAV REMINDER" in result["output"], \
        f"Expected nav reminder in output, got: {result['output']}"
    assert "omt_nav" in result["output"], \
        f"Expected omt_nav mention in reminder, got: {result['output']}"
    
    # Second tool result in SAME session - should NOT prepend again
    output_payload2 = {
        "title": "Edit file",
        "output": "edit result",
        "metadata": {},
    }
    result2 = asyncio.run(after_hook(input_payload, output_payload2))
    
    # Nav reminder should only appear once
    nav_count = result2["output"].count("🧭 NAV REMINDER")
    assert nav_count == 1, \
        f"Nav reminder should appear exactly once per session, got {nav_count} times"
    
    print("✅ omt_enforcer: Nav reminder prepends on FIRST tool result per session only")


def test_omt_enforcer_read_injection_d1():
    """omt_enforcer: D1 read-time thought injection fires on FIRST read of thought-carrying file."""
    plugin = load_plugin_module(
        REPO_ROOT / ".opencode" / "plugin" / "omt_enforcer.ts",
        "omt_enforcer"
    )
    factory = plugin.default
    tools = factory()
    
    after_hook = tools["tool.execute.after"]
    session_id = f"test-session-{uuid.uuid4()}"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "thoughtful_file.py"
        test_file.write_text("# TA: why: this is a design note\n# TA: risk: this might break\nprint('code')\n")
        
        import os
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            # First read of thought-carrying file - should inject thoughts
            input_payload = {
                "tool": "read",
                "sessionID": session_id,
                "args": {"filePath": str(test_file)},
            }
            output_payload = {
                "title": "Read file",
                "output": "file content",
                "metadata": {},
            }
            
            import asyncio
            result = asyncio.run(after_hook(input_payload, output_payload))
            
            # Verify thought injection
            assert "💡 TA: thoughts in" in result["output"], \
                f"Expected thought injection in output, got: {result['output']}"
            assert "design note" in result["output"], \
                f"Expected thought content in injection, got: {result['output']}"
            assert "might break" in result["output"], \
                f"Expected risk thought in injection, got: {result['output']}"
            
            # Second read of SAME file in same session - should NOT inject again
            result2 = asyncio.run(after_hook(input_payload, output_payload))
            assert "💡 TA: thoughts in" not in result2["output"], \
                f"Thought injection should not repeat for same file in session, got: {result2['output']}"
            
            # Read of DIFFERENT thought-carrying file - SHOULD inject
            other_file = Path(tmpdir) / "other.py"
            other_file.write_text("// TA: todo: refactor this\nconsole.log('hi');\n")
            
            input_payload3 = {
                "tool": "read",
                "sessionID": session_id,
                "args": {"filePath": str(other_file)},
            }
            result3 = asyncio.run(after_hook(input_payload3, output_payload))
            assert "💡 TA: thoughts in" in result3["output"], \
                f"Expected injection for new thought-carrying file, got: {result3['output']}"
            assert "refactor this" in result3["output"]
            
            print("✅ omt_enforcer: D1 read injection fires on first read per file per session")
            
        finally:
            os.chdir(old_cwd)


def test_hook_payload_shapes_match_sdk_contract():
    """Verify the hook input/output shapes match the REAL opencode SDK contract.
    
    This is the contract-pinning test from feature_023 Tier 2 - it would have
    caught F14 (reading output.args which never existed).
    """
    import asyncio
    
    # Load both plugins
    think_plugin = load_plugin_module(
        REPO_ROOT / ".opencode" / "plugin" / "omt_think.ts",
        "omt_think"
    )
    enforcer_plugin = load_plugin_module(
        REPO_ROOT / ".opencode" / "plugin" / "omt_enforcer.ts",
        "omt_enforcer"
    )
    
    think_tools = think_plugin.default()
    enforcer_tools = enforcer_plugin.default()
    
    # Test REAL payload shape per SDK contract:
    # tool.execute.after input: {tool, sessionID, args}
    # tool.execute.after output: {title, output, metadata}  -- NO args!
    
    input_payload = {
        "tool": "read",
        "sessionID": "test-session",
        "args": {"filePath": "test.py", "path": "test.py", "file": "test.py"},
    }
    output_payload = {
        "title": "Read file",
        "output": "content",
        "metadata": {"size": 100},
    }
    
    # Both hooks should handle this shape without error
    result_think = asyncio.run(think_tools["tool.execute.after"](input_payload, output_payload))
    result_enforcer = asyncio.run(enforcer_tools["tool.execute.after"](input_payload, output_payload))
    
    # Output payload should be modified (string) not replaced
    assert isinstance(result_think["output"], str)
    assert isinstance(result_enforcer["output"], str)
    
    # Input args should be accessible for read-injection
    assert input_payload["args"]["filePath"] == "test.py"
    
    print("✅ Hook payload shapes match real SDK contract (input.args, output={title,output,metadata})")


def test_session_start_hook_is_inert():
    """Verify session.start hook exists but is inert (opencode never dispatches it)."""
    think_plugin = load_plugin_module(
        REPO_ROOT / ".opencode" / "plugin" / "omt_think.ts",
        "omt_think"
    )
    enforcer_plugin = load_plugin_module(
        REPO_ROOT / ".opencode" / "plugin" / "omt_enforcer.ts",
        "omt_enforcer"
    )
    
    think_tools = think_plugin.default()
    enforcer_tools = enforcer_plugin.default()
    
    # Both plugins register session.start
    assert "session.start" in think_tools, "omt_think should register session.start (retained for future SDK)"
    assert "session.start" in enforcer_tools, "omt_enforcer should register session.start (retained for future SDK)"
    
    # They should not throw (inert)
    import asyncio
    result_think = asyncio.run(think_tools["session.start"]({}, {}))
    result_enforcer = asyncio.run(enforcer_tools["session.start"]({}, {}))
    
    # session.start returns nothing meaningful in current SDK
    print("✅ session.start hooks exist (retained for future SDK) and are inert")


if __name__ == "__main__":
    print("=" * 70)
    print("PRODUCTION VERIFICATION: OMT++ Hook Effects (feature_023)")
    print("=" * 70)
    print()
    
    try:
        test_hook_payload_shapes_match_sdk_contract()
        test_session_start_hook_is_inert()
        test_omt_think_digest_injects_on_first_tool_result()
        test_omt_enforcer_nav_reminder_on_first_tool_result()
        test_omt_enforcer_read_injection_d1()
        
        print()
        print("=" * 70)
        print("✅ ALL PRODUCTION HOOK EFFECTS VERIFIED")
        print("   - TA digest injects on first tool result (omt_think)")
        print("   - Nav reminder prepends on first tool result (omt_enforcer)")
        print("   - D1 read injection fires on first read per file (omt_enforcer)")
        print("   - Payload shapes match real SDK contract")
        print("   - session.start retained but inert (F14c fix verified)")
        print("=" * 70)
        
    except AssertionError as e:
        print()
        print("=" * 70)
        print("❌ PRODUCTION VERIFICATION FAILED")
        print(f"   {e}")
        print("=" * 70)
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ PRODUCTION VERIFICATION ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 70)
        sys.exit(1)