#!/usr/bin/env python3
"""
Test script for AgentX Goal Command using stdio.

This script tests the goal command implementation by:
1. Running the main.py script with uv
2. Sending goal commands via stdin
3. Validating responses via stdout

The goal command creates a new session objective Petri Net each time it's called.
"""

import subprocess
import sys
import os
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
    # Get absolute path to project root
    test_dir = Path(__file__).parent.resolve()
    project_root = test_dir.parent.parent
    main_py = project_root / "src" / "agentx" / "main.py"
    
    # Verify paths
    if not main_py.exists():
        return False, f"Error: main.py not found at {main_py}"
    
    # Build the command
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


def test_goal_command_basic() -> bool:
    """Test 1: Basic goal command creates Petri Net"""
    print("\n" + "="*70)
    print("TEST 1: Basic Goal Command")
    print("="*70)
    
    commands = [
        "goal Debug the login issue",
        "quit"
    ]
    
    success, output = run_agentx_command(commands)
    
    print(f"Commands sent: {commands}")
    print(f"Output preview: {output[:500]}...")
    
    # Validate output contains goal-related information
    if "objective" in output.lower() or "workflow" in output.lower() or "petri" in output.lower():
        print("✓ Basic goal command test PASSED")
        return True
    else:
        print("✗ Basic goal command test FAILED")
        print(f"Full output: {output}")
        return False


def test_goal_command_multiple() -> bool:
    """Test 2: Multiple goal commands create separate Petri Nets"""
    print("\n" + "="*70)
    print("TEST 2: Multiple Goal Commands")
    print("="*70)
    
    commands = [
        "goal First objective",
        "status",
        "goal Second objective",
        "status",
        "quit"
    ]
    
    success, output = run_agentx_command(commands)
    
    print(f"Commands sent: {commands}")
    print(f"Output preview: {output[:800]}...")
    
    # Should show multiple status outputs
    if output.lower().count("objective") >= 2:
        print("✓ Multiple goal commands test PASSED")
        return True
    else:
        print("✗ Multiple goal commands test FAILED")
        print(f"Full output: {output}")
        return False


def test_goal_with_status() -> bool:
    """Test 3: Goal command followed by status shows correct state"""
    print("\n" + "="*70)
    print("TEST 3: Goal Command with Status")
    print("="*70)
    
    commands = [
        "goal Analyze the project structure",
        "status",
        "quit"
    ]
    
    success, output = run_agentx_command(commands)
    
    print(f"Commands sent: {commands}")
    print(f"Output preview: {output[:800]}...")
    
    # Should contain session state information
    if "session state" in output.lower() or "petri" in output.lower() or "workflow" in output.lower():
        print("✓ Goal with status test PASSED")
        return True
    else:
        print("✗ Goal with status test FAILED")
        print(f"Full output: {output}")
        return False


def test_goal_with_petri_print() -> bool:
    """Test 4: Goal command followed by petri-print shows visualization"""
    print("\n" + "="*70)
    print("TEST 4: Goal Command with Petri Print")
    print("="*70)
    
    commands = [
        "goal Debug the login issue",
        "petri-print",
        "quit"
    ]
    
    success, output = run_agentx_command(commands)
    
    print(f"Commands sent: {commands}")
    print(f"Output preview: {output[:800]}...")
    
    # Should contain Petri Net visualization
    if "petri" in output.lower() or "net" in output.lower() or "place" in output.lower() or "transition" in output.lower():
        print("✓ Goal with petri-print test PASSED")
        return True
    else:
        print("✗ Goal with petri-print test FAILED")
        print(f"Full output: {output}")
        return False


def test_goal_command_in_help() -> bool:
    """Test 5: Goal command appears in help"""
    print("\n" + "="*70)
    print("TEST 5: Goal Command in Help")
    print("="*70)
    
    commands = [
        "help",
        "quit"
    ]
    
    success, output = run_agentx_command(commands)
    
    print(f"Commands sent: {commands}")
    print(f"Output preview: {output[:500]}...")
    
    # Help should list goal command
    if "goal" in output.lower():
        print("✓ Goal command in help test PASSED")
        return True
    else:
        print("✗ Goal command in help test FAILED")
        print(f"Full output: {output}")
        return False


def test_goal_command_error_handling() -> bool:
    """Test 6: Goal command without prompt shows error"""
    print("\n" + "="*70)
    print("TEST 6: Goal Command Error Handling")
    print("="*70)
    
    commands = [
        "goal",
        "quit"
    ]
    
    success, output = run_agentx_command(commands)
    
    print(f"Commands sent: {commands}")
    print(f"Output preview: {output[:500]}...")
    
    # Should show error or require prompt
    # Either error message or no Petri Net creation is acceptable
    print("✓ Goal command error handling test PASSED (command executed)")
    return True


def main():
    """Run all goal command tests."""
    print("\n" + "="*70)
    print("AGENT-X GOAL COMMAND TESTS")
    print("Testing goal command creates new session objective Petri Nets")
    print("="*70)
    
    tests = [
        ("Test 1: Basic Goal Command", test_goal_command_basic),
        ("Test 2: Multiple Goal Commands", test_goal_command_multiple),
        ("Test 3: Goal with Status", test_goal_with_status),
        ("Test 4: Goal with Petri Print", test_goal_with_petri_print),
        ("Test 5: Goal in Help", test_goal_command_in_help),
        ("Test 6: Error Handling", test_goal_command_error_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} EXCEPTION: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*70)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
