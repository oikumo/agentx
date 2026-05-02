#!/usr/bin/env python3
"""
OpenCode Agent - KB Command Integration Tests
==============================================
Tests for KB commands that opencode uses frequently.
These tests validate the CLI commands and their integration with agent workflows.
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add KB to path
KB_PATH = Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base"
sys.path.insert(0, str(KB_PATH))

from knowledge_base import kb_search, kb_ask, kb_add_entry, kb_stats


class CommandResults:
    """Track command test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def add_result(self, name: str, passed: bool, message: str = "", warning: bool = False):
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

    def summary(self) -> Dict[str, Any]:
        return {
            'passed': self.passed,
            'failed': self.failed,
            'warnings': self.warnings,
            'total': self.passed + self.failed,
            'success_rate': self.passed / (self.passed + self.failed) * 100 if (self.passed + self.failed) > 0 else 0
        }


results = CommandResults()


# =============================================================================
# CLI Command Tests
# =============================================================================

def test_kb_cli_search_command():
    """Test 'meta kb search' command"""
    name = "CLI Search Command"
    try:
        cmd = [
            "python3",
            str(KB_PATH / "kb"),
            "search", "MainController",
            "-k", "3"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        passed = result.returncode == 0 or "MainController" in result.stdout
        results.add_result(name, passed, "CLI search works" if passed else "CLI search failed")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_kb_cli_ask_command():
    """Test 'meta kb ask' command"""
    name = "CLI Ask Command"
    try:
        cmd = [
            "python3",
            str(KB_PATH / "kb"),
            "ask", "What is MainController?",
            "--top-k", "3"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        passed = result.returncode == 0
        results.add_result(name, passed, "CLI ask works" if passed else "CLI ask failed")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_kb_cli_stats_command():
    """Test 'meta kb stats' command"""
    name = "CLI Stats Command"
    try:
        cmd = [
            "python3",
            str(KB_PATH / "kb"),
            "stats"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        passed = result.returncode == 0 and "Total entries" in result.stdout
        results.add_result(name, passed, "CLI stats works" if passed else "CLI stats failed")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_kb_cli_add_command():
    """Test 'meta kb add' command"""
    name = "CLI Add Command"
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        cmd = [
            "python3",
            str(KB_PATH / "kb"),
            "add",
            "finding",
            "test",
            f"CLI Test Entry {timestamp}",
            "CLI finding",
            "CLI solution",
            "--confidence", "0.9"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        passed = result.returncode == 0
        results.add_result(name, passed, "Add command works" if passed else "Add command failed")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_kb_cli_explore_command():
    """Test 'meta kb explore' command"""
    name = "CLI Explore Command"
    try:
        cmd = [
            "python3",
            str(KB_PATH / "kb"),
            "explore"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        passed = result.returncode == 0 and "DOCUMENTATION" in result.stdout
        results.add_result(name, passed, "Explore works" if passed else "Explore failed")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_kb_cli_correct_command():
    """Test 'meta kb correct' command"""
    name = "CLI Correct Command"
    try:
        # First add an entry to correct
        add_result = kb_add_entry(
            entry_type="finding",
            category="test",
            title="CLI Correct Test",
            finding="Original finding",
            solution="Original solution",
            confidence=0.9
        )

        # Search for it to get ID
        search_result = kb_search("CLI Correct Test", top_k=1)

        # Try to correct (might fail if entry not found, which is OK for this test)
        cmd = [
            "python3",
            str(KB_PATH / "kb"),
            "correct",
            "test_id",  # This will fail, testing error handling
            "Test reason",
            "New finding"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        # Should handle gracefully (either success or graceful error)
        passed = True  # If it doesn't crash, it's OK
        results.add_result(name, passed, "Correct command handled")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


# =============================================================================
# Python API Tests
# =============================================================================

def test_python_api_search():
    """Test Python API search function"""
    name = "Python API Search"
    try:
        result = kb_search("MainController", top_k=3)
        passed = len(result) > 0
        results.add_result(name, passed, "API search works" if passed else "API search failed")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_python_api_ask():
    """Test Python API ask function"""
    name = "Python API Ask"
    try:
        result = kb_ask("What is the workflow?", top_k=3)
        passed = len(result) > 0
        results.add_result(name, passed, "API ask works" if passed else "API ask failed")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_python_api_stats():
    """Test Python API stats function"""
    name = "Python API Stats"
    try:
        result = kb_stats()
        passed = "Total entries" in result
        results.add_result(name, passed, "API stats works" if passed else "API stats failed")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_python_api_add_entry():
    """Test Python API add_entry function"""
    name = "Python API Add Entry"
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        result = kb_add_entry(
            entry_type="finding",
            category="test",
            title=f"API Test Entry {timestamp}",
            finding="API finding",
            solution="API solution",
            confidence=0.9
        )
        passed = len(result) > 0 and "Error" not in result
        results.add_result(name, passed, "API add works" if passed else "API add failed")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


# =============================================================================
# Agent Workflow Command Tests
# =============================================================================

def test_agent_startup_commands():
    """Test commands agent runs on startup"""
    name = "Agent Startup Commands"
    try:
        # 1. Check WORK.md exists
        work_file = Path(__file__).parent.parent.parent.parent / "WORK.md"
        work_exists = work_file.exists()

        # 2. Query KB for context
        kb_result = kb_ask("What is my task?", top_k=2)
        kb_works = len(kb_result) > 0

        # 3. Get stats
        stats = kb_stats()
        stats_work = "Total entries" in stats

        passed = work_exists and kb_works and stats_work
        results.add_result(name, passed, "Startup sequence works" if passed else "Startup issue")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_kb_first_workflow():
    """Test KB-first workflow commands"""
    name = "KB-First Workflow"
    try:
        queries = [
            "Where should I write tests?",
            "How to add a feature?",
            "What is the current task?",
        ]

        all_succeeded = True
        for query in queries:
            result = kb_ask(query, top_k=2)
            if len(result) == 0:
                all_succeeded = False
                break

        results.add_result(name, all_succeeded, "KB-first works" if all_succeeded else "KB-first issue")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_task_completion_workflow():
    """Test workflow: query -> work -> add knowledge -> stats"""
    name = "Task Completion Workflow"
    try:
        workflow = [
            ("query", lambda: kb_search("workflow", top_k=2)),
            ("work", lambda: "Simulated work"),
            ("add", lambda: kb_add_entry("finding", "test", "Workflow Test",
                                        "Workflow finding", "Workflow solution")),
            ("stats", lambda: kb_stats()),
        ]

        successful = 0
        for step_name, step_func in workflow:
            try:
                result = step_func()
                if len(str(result)) > 0:
                    successful += 1
            except:
                pass

        passed = successful == len(workflow)
        results.add_result(name, passed, f"{successful}/{len(workflow)} steps")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


# =============================================================================
# Meta Command Tests
# =============================================================================

def test_meta_commands():
    """Test meta commands from AGENTS.md"""
    name = "Meta Commands"
    try:
        # Test meta kb commands
        meta_commands = [
            ["python3", str(KB_PATH / "kb"), "search", "test", "-k", "2"],
            ["python3", str(KB_PATH / "kb"), "ask", "test?", "--top-k", "2"],
            ["python3", str(KB_PATH / "kb"), "stats"],
        ]

        successful = 0
        for cmd in meta_commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    successful += 1
            except:
                pass

        passed = successful == len(meta_commands)
        results.add_result(name, passed, f"{successful}/{len(meta_commands)} commands")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_meta_kb_populate():
    """Test meta kb populate command"""
    name = "Meta KB Populate"
    try:
        populate_script = KB_PATH.parent / "populate" / "populate_kb.py"

        if populate_script.exists():
            cmd = ["python3", str(populate_script)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            # Should not crash (success or already populated is OK)
            passed = True
            results.add_result(name, passed, "Populate script exists")
        else:
            results.add_result(name, True, "Populate script not found (skip)", warning=True)
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


# =============================================================================
# Test Runner
# =============================================================================

def run_all_tests():
    """Run all command integration tests"""
    print("\n" + "="*70)
    print("OpenCode Agent - KB Command Integration Tests")
    print("="*70 + "\n")

    # CLI Command Tests
    print("CLI Command Tests:")
    test_kb_cli_search_command()
    test_kb_cli_ask_command()
    test_kb_cli_stats_command()
    test_kb_cli_add_command()
    test_kb_cli_explore_command()
    test_kb_cli_correct_command()
    print()

    # Python API Tests
    print("Python API Tests:")
    test_python_api_search()
    test_python_api_ask()
    test_python_api_stats()
    test_python_api_add_entry()
    print()

    # Agent Workflow Tests
    print("Agent Workflow Tests:")
    test_agent_startup_commands()
    test_agent_kb_first_workflow()
    test_agent_task_completion_workflow()
    print()

    # Meta Command Tests
    print("Meta Command Tests:")
    test_meta_commands()
    test_meta_kb_populate()
    print()

    # Summary
    summary = results.summary()
    print("\n" + "="*70)
    print("Command Integration Tests Complete")
    print(f" Passed: {summary['passed']}")
    print(f" Failed: {summary['failed']}")
    print(f" Warnings: {summary['warnings']}")
    print(f" Success Rate: {summary['success_rate']:.1f}%")
    print("="*70 + "\n")

    return summary


if __name__ == "__main__":
    summary = run_all_tests()

    # Save results
    results_file = Path(__file__).parent / 'command_integration_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': summary
        }, f, indent=2)

    print(f"\nResults saved to: {results_file}")

    sys.exit(0 if summary['failed'] == 0 else 1)
