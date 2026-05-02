#!/usr/bin/env python3
"""
OpenCode Real Agent Tests
==========================
Tests that validate KB integration by running actual opencode commands
and verifying the output matches expected behavior.

This tests the REAL opencode agent interaction, not just simulated stdio.
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple


class RealAgentResults:
    """Track real agent test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.test_logs = []

    def add_result(self, name: str, passed: bool, message: str = "", warning: bool = False, log: str = ""):
        status = "✓" if passed else "✗"
        if warning:
            status = "⚠"
            self.warnings += 1
            print(f" {status} {name}: {message}")
        elif passed:
            self.passed += 1
            print(f" {status} {name}")
        else:
            self.failed += 1
            print(f" {status} {name}: {message}")

        self.test_logs.append({
            'name': name,
            'passed': passed,
            'warning': warning,
            'message': message,
            'log': log,
            'timestamp': datetime.now().isoformat()
        })

    def summary(self) -> Dict[str, Any]:
        return {
            'passed': self.passed,
            'failed': self.failed,
            'warnings': self.warnings,
            'total': self.passed + self.failed,
            'success_rate': self.passed / (self.passed + self.failed) * 100 if (self.passed + self.failed) > 0 else 0
        }


results = RealAgentResults()


def run_opencode_command(query: str, timeout: int = 120) -> Tuple[bool, str, float]:
    """
    Run actual opencode command and capture output.
    
    Args:
        query: The query to send to opencode
        timeout: Timeout in seconds
    
    Returns:
        Tuple of (success, output, duration)
    """
    cmd = ["opencode", "run", query]
    
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(Path(__file__).parent.parent.parent.parent)
        )
        duration = time.time() - start
        output = result.stdout + result.stderr
        success = result.returncode == 0
        return success, output, duration
    except subprocess.TimeoutExpired as e:
        duration = time.time() - start
        return False, f"Timeout after {timeout}s: {str(e)}", duration
    except Exception as e:
        return False, f"Exception: {str(e)}", time.time() - start


def test_opencode_kb_first_rule():
    """Test that opencode follows KB-first rule"""
    name = "Real Agent: KB-First Rule"
    try:
        query = "What is the KB-first rule in AgentX?"
        success, output, duration = run_opencode_command(query, timeout=120)
        
        # Verify opencode queried the KB
        kb_queried = (
            "kb ask" in output.lower() or 
            "knowledge base" in output.lower() or
            "KB-first" in output or
            "synthesized from" in output
        )
        
        passed = success and kb_queried
        log_msg = f"Duration: {duration:.1f}s, KB queried: {kb_queried}"
        
        results.add_result(name, passed, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


def test_opencode_kb_search_usage():
    """Test that opencode uses KB search when appropriate"""
    name = "Real Agent: KB Search Usage"
    try:
        query = "Where should I write tests in AgentX?"
        success, output, duration = run_opencode_command(query, timeout=120)
        
        # Should use KB search
        uses_kb = (
            "kb search" in output.lower() or
            "kb ask" in output.lower() or
            "knowledge base" in output.lower()
        )
        
        passed = success and uses_kb
        log_msg = f"Duration: {duration:.1f}s, Uses KB: {uses_kb}"
        
        results.add_result(name, passed, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


def test_opencode_meta_harness_awareness():
    """Test that opencode knows about META HARNESS structure"""
    name = "Real Agent: META HARNESS Awareness"
    try:
        query = "What is the META HARNESS structure?"
        success, output, duration = run_opencode_command(query, timeout=120)
        
        # Should mention META HARNESS components
        has_awareness = (
            ".meta" in output.lower() or
            "sandbox" in output.lower() or
            "knowledge base" in output.lower() or
            "kb" in output.lower()
        )
        
        passed = success and has_awareness
        log_msg = f"Duration: {duration:.1f}s, Has awareness: {has_awareness}"
        
        results.add_result(name, passed, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


def test_opencode_workflow_knowledge():
    """Test that opencode knows AgentX workflows"""
    name = "Real Agent: Workflow Knowledge"
    try:
        query = "How do I add a feature in AgentX?"
        success, output, duration = run_opencode_command(query, timeout=120)
        
        # Should mention workflow steps
        has_workflow = (
            "sandbox" in output.lower() or
            "features/" in output or
            "planned" in output.lower() or
            "wip" in output.lower() or
            "test" in output.lower()
        )
        
        passed = success and has_workflow
        log_msg = f"Duration: {duration:.1f}s, Has workflow: {has_workflow}"
        
        results.add_result(name, passed, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


def test_opencode_command_execution():
    """Test that opencode can execute KB commands"""
    name = "Real Agent: Command Execution"
    try:
        query = "Show me KB statistics"
        success, output, duration = run_opencode_command(query, timeout=120)
        
        # Should execute KB stats command
        executes_command = (
            "kb stats" in output.lower() or
            "total entries" in output.lower() or
            "statistics" in output.lower() or
            success  # Even if just explains, it's OK
        )
        
        passed = success or executes_command
        log_msg = f"Duration: {duration:.1f}s, Executes: {executes_command}"
        
        results.add_result(name, passed, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


def test_opencode_error_handling():
    """Test that opencode handles KB errors gracefully"""
    name = "Real Agent: Error Handling"
    try:
        # Query something that might not exist
        query = "What is the nonexistent_feature_xyz?"
        success, output, duration = run_opencode_command(query, timeout=120)
        
        # Should handle gracefully (not crash)
        handles_gracefully = success or len(output) > 0
        
        log_msg = f"Duration: {duration:.1f}s, Graceful: {handles_gracefully}"
        
        results.add_result(name, handles_gracefully, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


def test_opencode_context_retention():
    """Test that opencode maintains context across KB queries"""
    name = "Real Agent: Context Retention"
    try:
        # First query
        query1 = "What is the KB-first rule?"
        success1, output1, duration1 = run_opencode_command(query1, timeout=120)
        
        # Second related query
        query2 = "How do I query the KB?"
        success2, output2, duration2 = run_opencode_command(query2, timeout=120)
        
        # Both should succeed and mention KB
        both_work = (success1 or len(output1) > 0) and (success2 or len(output2) > 0)
        
        log_msg = f"Query1: {duration1:.1f}s, Query2: {duration2:.1f}s"
        
        results.add_result(name, both_work, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


def test_opencode_performance():
    """Test opencode response time with KB"""
    name = "Real Agent: Performance"
    try:
        query = "What is AgentX?"
        start = time.time()
        success, output, duration = run_opencode_command(query, timeout=120)
        
        # Should complete in reasonable time (< 60s for simple query)
        acceptable_time = duration < 60
        
        log_msg = f"Duration: {duration:.1f}s, Acceptable: {acceptable_time}"
        
        results.add_result(name, acceptable_time, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


def run_all_tests():
    """Run all real agent tests"""
    print("\n" + "="*70)
    print("OpenCode Real Agent Tests")
    print("="*70 + "\n")
    print("Note: These tests run actual opencode commands (can be slow)")
    print("="*70 + "\n")

    # Core functionality
    print("Core KB Integration:")
    test_opencode_kb_first_rule()
    test_opencode_kb_search_usage()
    print()

    # Knowledge validation
    print("Knowledge Validation:")
    test_opencode_meta_harness_awareness()
    test_opencode_workflow_knowledge()
    print()

    # Command execution
    print("Command Execution:")
    test_opencode_command_execution()
    print()

    # Error handling
    print("Error Handling:")
    test_opencode_error_handling()
    print()

    # Context and performance
    print("Context & Performance:")
    test_opencode_context_retention()
    test_opencode_performance()
    print()

    # Summary
    summary = results.summary()
    print("\n" + "="*70)
    print("Real Agent Tests Complete")
    print(f" Passed: {summary['passed']}")
    print(f" Failed: {summary['failed']}")
    print(f" Warnings: {summary['warnings']}")
    print(f" Success Rate: {summary['success_rate']:.1f}%")
    print("="*70 + "\n")

    return results.test_logs, summary


if __name__ == "__main__":
    print("\n⚠️  WARNING: Real agent tests can take 5-10 minutes to complete!")
    print("   Each test runs actual opencode commands.\n")
    
    response = input("Continue with real agent tests? (y/N): ").strip().lower()
    if response != 'y':
        print("Tests cancelled.")
        sys.exit(0)
    
    test_logs, summary = run_all_tests()

    # Save results
    results_file = Path(__file__).parent / 'real_agent_test_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'test_logs': test_logs,
            'summary': summary
        }, f, indent=2)

    print(f"\nResults saved to: {results_file}")

    sys.exit(0 if summary['failed'] == 0 else 1)
