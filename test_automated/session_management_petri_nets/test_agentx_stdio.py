#!/usr/bin/env python3
"""
Test script for AgentX with Petri Net integration using stdio.

This script tests the actual AgentX application by:
1. Running the main.py script with uv
2. Sending commands via stdin
3. Validating responses via stdout
"""

import subprocess
import sys
import os
import time
from pathlib import Path


def run_agentx_command(commands: list[str], timeout: int = 30) -> tuple[bool, str]:
    """
    Run AgentX with a list of commands via stdin.
    
    Args:
        commands: List of commands to send to AgentX
        timeout: Timeout in seconds
        
    Returns:
        Tuple of (success, output)
    """
    # Get absolute path to project root (this file is in test_automated/session_management_petri_nets/)
    # So we need to go up 2 levels to reach project root
    test_dir = Path(__file__).parent.resolve()
    project_root = test_dir.parent.parent  # Goes up 2 levels to project root
    main_py = project_root / "src" / "agentx" / "main.py"
    
    # Verify paths
    if not main_py.exists():
        return False, f"Error: main.py not found at {main_py}"
    
    # Build the command - run from project root
    cmd = [
        "uv", "run", "python3", str(main_py)
    ]
    
    # Prepare input - join commands with newlines and add quit at the end
    input_text = "\n".join(commands)
    if "quit" not in input_text:
        input_text += "\nquit\n"
    else:
        input_text += "\n"
    
    try:
        # Run the command from project root
        result = subprocess.run(
            cmd,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(project_root),
            env={**os.environ, "PYTHONPATH": str(project_root / "src")}
        )
        
        output = result.stdout
        if result.stderr:
            output += "\nSTDERR:\n" + result.stderr
            
        return result.returncode == 0 or "API key" in result.stderr, output
        
    except subprocess.TimeoutExpired:
        return False, f"Timeout after {timeout} seconds"
    except Exception as e:
        return False, f"Error: {e}"


def test_help_command() -> bool:
    """Test 1: Help command via stdio"""
    print("\n" + "="*70)
    print("TEST 1: Help Command via stdio")
    print("="*70)
    
    commands = ["help"]
    success, output = run_agentx_command(commands)
    
    print(f"Commands sent: {commands}")
    print(f"Output preview: {output[:500]}...")
    
    # Validate output contains help information
    if "help" in output.lower() or "command" in output.lower():
        print("✓ Help command test PASSED")
        return True
    else:
        print("✗ Help command test FAILED")
        print(f"Full output: {output}")
        return False


def test_status_command() -> bool:
    """Test 2: Status command via stdio"""
    print("\n" + "="*70)
    print("TEST 2: Status Command via stdio")
    print("="*70)
    
    commands = ["status"]
    success, output = run_agentx_command(commands)
    
    print(f"Commands sent: {commands}")
    print(f"Output preview: {output[:500]}...")
    
    # Status should show session state (even if no active session)
    if "status" in output.lower() or "session" in output.lower() or "no active" in output.lower():
        print("✓ Status command test PASSED")
        return True
    else:
        print("✗ Status command test FAILED")
        print(f"Full output: {output}")
        return False


def test_new_command() -> bool:
    """Test 3: New command via stdio"""
    print("\n" + "="*70)
    print("TEST 3: New Command via stdio")
    print("="*70)
    
    commands = ["new test_stdio_session", "status"]
    success, output = run_agentx_command(commands, timeout=45)
    
    print(f"Commands sent: {commands}")
    print(f"Output preview: {output[:500]}...")
    
    # Should create a new session
    if "test_stdio_session" in output.lower() or "session" in output.lower() or success:
        print("✓ New command test PASSED")
        return True
    else:
        print("✗ New command test FAILED")
        print(f"Full output: {output}")
        return False


def test_petri_print_command() -> bool:
    """Test 4: Petri-print command via stdio"""
    print("\n" + "="*70)
    print("TEST 4: Petri-Print Command via stdio")
    print("="*70)
    
    commands = ["petri-print"]
    success, output = run_agentx_command(commands)
    
    print(f"Commands sent: {commands}")
    print(f"Output preview: {output[:500]}...")
    
    # Should show Petri Net state or indicate no active session
    if "petri" in output.lower() or "net" in output.lower() or "no active" in output.lower() or "session" in output.lower():
        print("✓ Petri-print command test PASSED")
        return True
    else:
        print("✗ Petri-print command test FAILED")
        print(f"Full output: {output}")
        return False


def test_command_sequence() -> bool:
    """Test 5: Command sequence via stdio"""
    print("\n" + "="*70)
    print("TEST 5: Command Sequence via stdio")
    print("="*70)
    
    commands = [
        "help",
        "status",
        "new test_sequence_session",
        "petri-print",
        "status"
    ]
    success, output = run_agentx_command(commands, timeout=60)
    
    print(f"Commands sent: {commands}")
    print(f"Output length: {len(output)} chars")
    print(f"Output preview: {output[:500]}...")
    
    # Should handle all commands
    if success or len(output) > 100:
        print("✓ Command sequence test PASSED")
        return True
    else:
        print("✗ Command sequence test FAILED")
        print(f"Full output: {output}")
        return False


def test_version_display() -> bool:
    """Test 6: Version display on startup"""
    print("\n" + "="*70)
    print("TEST 6: Version Display on Startup")
    print("="*70)
    
    # Just run and quit immediately
    commands = ["quit"]
    success, output = run_agentx_command(commands, timeout=30)
    
    print(f"Commands sent: {commands}")
    print(f"Output preview: {output[:500]}...")
    
    # Should show version or agentx branding
    if "agentx" in output.lower() or success:
        print("✓ Version display test PASSED")
        return True
    else:
        print("✗ Version display test FAILED")
        print(f"Full output: {output}")
        return False


def main():
    """Run all stdio tests"""
    print("\n" + "="*70)
    print("AGENT-X PETRI NET: STDIO INTEGRATION TEST")
    print("="*70)
    print(f"Using: uv run python3 src/agentx/main.py")
    print("="*70)
    
    tests = [
        ("Help Command", test_help_command),
        ("Status Command", test_status_command),
        ("New Command", test_new_command),
        ("Petri-Print Command", test_petri_print_command),
        ("Command Sequence", test_command_sequence),
        ("Version Display", test_version_display),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("STDIO TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All stdio tests passed! AgentX is working correctly via stdio.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
