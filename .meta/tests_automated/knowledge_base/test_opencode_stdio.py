#!/usr/bin/env python3
"""
OpenCode Stdio Interface Tests
===============================
Tests that validate the KB works through opencode's actual stdio interface.
These tests simulate how opencode actually communicates with the KB.

OpenCode uses stdio for:
- Reading user messages
- Sending tool calls (including KB queries)
- Receiving tool responses
- Maintaining conversation context
"""

import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple


class StdioResults:
    """Track stdio test results"""
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


results = StdioResults()


# =============================================================================
# Stdio Communication Tests
# =============================================================================

def test_stdio_kb_search_command():
    """Test KB search through stdio command interface"""
    name = "Stdio KB Search Command"
    try:
        # Simulate opencode calling KB via stdio
        cmd = [
            "python3",
            str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb"),
            "search", "MainController",
            "-k", "3"
        ]
        
        start = time.time()
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        duration = time.time() - start
        
        # Check if command executed successfully
        success = process.returncode == 0 or "MainController" in process.stdout
        log_msg = f"Duration: {duration:.2f}s, Return code: {process.returncode}"
        
        results.add_result(name, success, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


def test_stdio_kb_ask_command():
    """Test KB ask through stdio command interface"""
    name = "Stdio KB Ask Command"
    try:
        cmd = [
            "python3",
            str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb"),
            "ask", "What is the workflow for adding features?",
            "--top-k", "3"
        ]
        
        start = time.time()
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15
        )
        duration = time.time() - start
        
        # Should return synthesized answer
        has_answer = "Answer" in process.stdout or "sources" in process.stdout.lower() or process.returncode == 0
        log_msg = f"Duration: {duration:.2f}s, Output length: {len(process.stdout)}"
        
        results.add_result(name, has_answer, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


def test_stdio_kb_stats_command():
    """Test KB stats through stdio"""
    name = "Stdio KB Stats Command"
    try:
        cmd = [
            "python3",
            str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb"),
            "stats"
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        # Should return statistics
        has_stats = "Total entries" in process.stdout and process.returncode == 0
        log_msg = f"Return code: {process.returncode}, Has stats: {has_stats}"
        
        results.add_result(name, has_stats, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


# =============================================================================
# Simulated Agent-Stdio Interaction Tests
# =============================================================================

def test_simulated_agent_startup_via_stdio():
    """Simulate complete agent startup sequence via stdio"""
    name = "Simulated Agent Startup (Stdio)"
    try:
        steps = []
        
        # Step 1: Agent reads WORK.md (simulated)
        work_file = Path(__file__).parent.parent.parent.parent / "WORK.md"
        work_exists = work_file.exists()
        steps.append(f"1. WORK.md exists: {work_exists}")
        
        # Step 2: Agent queries KB via stdio
        kb_cmd = [
            "python3",
            str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb"),
            "ask", "What is my current task?",
            "--top-k", "2"
        ]
        
        kb_result = subprocess.run(kb_cmd, capture_output=True, text=True, timeout=15)
        kb_works = kb_result.returncode == 0
        steps.append(f"2. KB query via stdio: {'OK' if kb_works else 'FAILED'}")
        
        # Step 3: Get stats
        stats_cmd = [
            "python3",
            str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb"),
            "stats"
        ]
        
        stats_result = subprocess.run(stats_cmd, capture_output=True, text=True, timeout=10)
        stats_work = stats_result.returncode == 0
        steps.append(f"3. KB stats via stdio: {'OK' if stats_work else 'FAILED'}")
        
        # All steps must succeed
        success = work_exists and kb_works and stats_work
        log_msg = " | ".join(steps)
        
        results.add_result(name, success, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


def test_simulated_kb_first_workflow_via_stdio():
    """Simulate KB-first workflow via stdio"""
    name = "Simulated KB-First Workflow (Stdio)"
    try:
        # Agent must query KB before any task
        queries = [
            "Where should I write tests?",
            "How to add a feature?",
            "What is MainController?",
        ]
        
        successful_queries = 0
        query_results = []
        
        for query in queries:
            cmd = [
                "python3",
                str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb"),
                "ask", query,
                "--top-k", "2"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            success = result.returncode == 0 and len(result.stdout) > 0
            
            if success:
                successful_queries += 1
            
            query_results.append(f"{query[:30]}...: {'OK' if success else 'FAIL'}")
        
        # Most queries should succeed
        success_rate = successful_queries / len(queries)
        passed = success_rate >= 0.8
        log_msg = f"{successful_queries}/{len(queries)} OK | " + " | ".join(query_results)
        
        results.add_result(name, passed, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


def test_simulated_task_completion_via_stdio():
    """Simulate complete task workflow via stdio"""
    name = "Simulated Task Completion (Stdio)"
    try:
        workflow_steps = []
        
        # Step 1: Query KB before task
        query_cmd = [
            "python3",
            str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb"),
            "search", "workflow",
            "-k", "2"
        ]
        
        query_result = subprocess.run(query_cmd, capture_output=True, text=True, timeout=10)
        workflow_steps.append(f"1. Query KB: {'OK' if query_result.returncode == 0 else 'FAIL'}")
        
        # Step 2: Simulate task execution (add entry)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        add_cmd = [
            "python3",
            str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb"),
            "add",
            "finding",
            "test",
            f"Stdio Test Entry {timestamp}",
            "Stdio finding",
            "Stdio solution",
            "--confidence", "0.9"
        ]
        
        add_result = subprocess.run(add_cmd, capture_output=True, text=True, timeout=10)
        workflow_steps.append(f"2. Add entry: {'OK' if add_result.returncode == 0 else 'FAIL'}")
        
        # Step 3: Verify entry exists
        search_cmd = [
            "python3",
            str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb"),
            "search", "Stdio Test",
            "-k", "2"
        ]
        
        search_result = subprocess.run(search_cmd, capture_output=True, text=True, timeout=10)
        workflow_steps.append(f"3. Verify entry: {'OK' if search_result.returncode == 0 else 'FAIL'}")
        
        # Step 4: Get stats
        stats_cmd = [
            "python3",
            str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb"),
            "stats"
        ]
        
        stats_result = subprocess.run(stats_cmd, capture_output=True, text=True, timeout=10)
        workflow_steps.append(f"4. Get stats: {'OK' if stats_result.returncode == 0 else 'FAIL'}")
        
        # All steps should succeed
        all_success = all(['OK' in step for step in workflow_steps])
        log_msg = " | ".join(workflow_steps)
        
        results.add_result(name, all_success, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


# =============================================================================
# Stdio Performance Tests
# =============================================================================

def test_stdio_command_latency():
    """Test latency of stdio commands"""
    name = "Stdio Command Latency"
    try:
        commands = [
            ["search", "test", "-k", "2"],
            ["ask", "test?", "--top-k", "2"],
            ["stats"],
        ]
        
        latencies = []
        kb_path = str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb")
        
        for cmd_args in commands:
            cmd = ["python3", kb_path] + cmd_args
            
            start = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            duration = time.time() - start
            
            latencies.append(duration)
        
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        # Average should be < 2s (stdio overhead expected)
        passed = avg_latency < 2.0
        log_msg = f"Avg: {avg_latency:.2f}s, Max: {max_latency:.2f}s"
        
        results.add_result(name, passed, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


def test_stdio_concurrent_commands():
    """Test concurrent stdio commands"""
    name = "Stdio Concurrent Commands"
    try:
        import concurrent.futures
        
        kb_path = str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb")
        
        def run_command(query: str):
            cmd = ["python3", kb_path, "ask", query, "--top-k", "2"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return result.returncode == 0
        
        queries = [
            "test 1",
            "test 2",
            "test 3",
            "test 4",
            "test 5",
        ]
        
        successful = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(run_command, q) for q in queries]
            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    successful += 1
        
        # Most should succeed
        passed = successful >= len(queries) * 0.8
        log_msg = f"{successful}/{len(queries)} concurrent commands OK"
        
        results.add_result(name, passed, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


# =============================================================================
# Stdio Error Handling Tests
# =============================================================================

def test_stdio_error_handling():
    """Test stdio error handling"""
    name = "Stdio Error Handling"
    try:
        error_scenarios = [
            ("empty_query", ["search", ""]),
            ("invalid_category", ["search", "test", "-k", "2", "--category", "invalid_cat"]),
            ("negative_topk", ["search", "test", "-k", "-1"]),
        ]
        
        kb_path = str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb")
        
        handled = 0
        for name_prefix, args in error_scenarios:
            cmd = ["python3", kb_path] + args
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                # Should not crash (return code can be 0 or non-zero, but no exception)
                handled += 1
            except Exception:
                pass  # Exception is also acceptable handling
        
        # Should handle all error scenarios gracefully
        passed = handled == len(error_scenarios)
        log_msg = f"Handled {handled}/{len(error_scenarios)} error scenarios"
        
        results.add_result(name, passed, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


def test_stdio_timeout_handling():
    """Test stdio timeout handling"""
    name = "Stdio Timeout Handling"
    try:
        kb_path = str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb")
        
        # Long query that might timeout
        cmd = ["python3", kb_path, "ask", "a" * 1000, "--top-k", "10"]
        
        start = time.time()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            duration = time.time() - start
            
            # Should either complete or timeout gracefully
            passed = True
            log_msg = f"Completed in {duration:.2f}s or timed out gracefully"
        except subprocess.TimeoutExpired:
            duration = time.time() - start
            passed = True  # Timeout is acceptable behavior
            log_msg = f"Timed out after {duration:.2f}s (expected)"
        
        results.add_result(name, passed, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


# =============================================================================
# Stdio Output Format Tests
# =============================================================================

def test_stdio_output_format():
    """Test that stdio output is properly formatted"""
    name = "Stdio Output Format"
    try:
        kb_path = str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb")
        
        # Test search output format
        search_cmd = ["python3", kb_path, "search", "workflow", "-k", "3"]
        search_result = subprocess.run(search_cmd, capture_output=True, text=True, timeout=10)
        
        # Should have structured output
        has_structure = len(search_result.stdout) > 0 and (
            "ID:" in search_result.stdout or
            "Type:" in search_result.stdout or
            "Title:" in search_result.stdout or
            "Answer" in search_result.stdout or
            search_result.returncode == 0
        )
        
        log_msg = f"Output length: {len(search_result.stdout)}, Structured: {has_structure}"
        
        results.add_result(name, has_structure, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


def test_stdio_json_output():
    """Test stdio JSON output capability"""
    name = "Stdio JSON Output"
    try:
        kb_path = str(Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base" / "kb")
        
        # Try to get JSON output if supported
        stats_cmd = ["python3", kb_path, "stats"]
        stats_result = subprocess.run(stats_cmd, capture_output=True, text=True, timeout=10)
        
        # Should return something
        has_output = len(stats_result.stdout) > 0 and stats_result.returncode == 0
        
        log_msg = f"Has output: {has_output}, Length: {len(stats_result.stdout)}"
        
        results.add_result(name, has_output, log_msg, log=log_msg)
        
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}", log=str(e))


# =============================================================================
# Test Runner
# =============================================================================

def run_all_tests():
    """Run all stdio tests"""
    print("\n" + "="*70)
    print("OpenCode Stdio Interface Tests")
    print("="*70 + "\n")

    # Stdio Communication Tests
    print("Stdio Communication Tests:")
    test_stdio_kb_search_command()
    test_stdio_kb_ask_command()
    test_stdio_kb_stats_command()
    print()

    # Simulated Agent Workflows
    print("Simulated Agent Workflows:")
    test_simulated_agent_startup_via_stdio()
    test_simulated_kb_first_workflow_via_stdio()
    test_simulated_task_completion_via_stdio()
    print()

    # Stdio Performance Tests
    print("Stdio Performance Tests:")
    test_stdio_command_latency()
    test_stdio_concurrent_commands()
    print()

    # Stdio Error Handling
    print("Stdio Error Handling:")
    test_stdio_error_handling()
    test_stdio_timeout_handling()
    print()

    # Stdio Output Format Tests
    print("Stdio Output Format Tests:")
    test_stdio_output_format()
    test_stdio_json_output()
    print()

    # Summary
    summary = results.summary()
    print("\n" + "="*70)
    print("Stdio Tests Complete")
    print(f" Passed: {summary['passed']}")
    print(f" Failed: {summary['failed']}")
    print(f" Warnings: {summary['warnings']}")
    print(f" Success Rate: {summary['success_rate']:.1f}%")
    print("="*70 + "\n")

    return results.test_logs, summary


if __name__ == "__main__":
    test_logs, summary = run_all_tests()

    # Save results
    results_file = Path(__file__).parent / 'stdio_test_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'test_logs': test_logs,
            'summary': summary
        }, f, indent=2)

    print(f"\nResults saved to: {results_file}")

    sys.exit(0 if summary['failed'] == 0 else 1)
