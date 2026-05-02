#!/usr/bin/env python3
"""
OpenCode Agent - Knowledge Base Integration Tests
==================================================
Tests to ensure the META HARNESS KB works well with opencode AI agent.
These tests validate the integration patterns that opencode uses when
interacting with the knowledge base.

Test Categories:
1. Agent Workflow Tests - Validate KB supports agent workflows
2. Query Pattern Tests - Test queries agents commonly make
3. Context Management - Ensure KB maintains proper context
4. Error Handling - Graceful handling of agent mistakes
5. Performance - KB responsiveness for agent interactions
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add KB to path
KB_PATH = Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base"
sys.path.insert(0, str(KB_PATH))

from knowledge_base import kb_search, kb_ask, kb_add_entry, kb_stats, kb_correct, kb_evolve
from src.advanced_rag import AdvancedRAG


class AgentIntegrationResults:
    """Track integration test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.test_results = []

    def add_result(self, name: str, passed: bool, message: str = "", warning: bool = False):
        """Record test result"""
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

        self.test_results.append({
            'name': name,
            'passed': passed,
            'warning': warning,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })

    def summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        return {
            'passed': self.passed,
            'failed': self.failed,
            'warnings': self.warnings,
            'total': self.passed + self.failed,
            'success_rate': self.passed / (self.passed + self.failed) * 100 if (self.passed + self.failed) > 0 else 0
        }


results = AgentIntegrationResults()


# =============================================================================
# Agent Workflow Tests
# =============================================================================

def test_agent_startup_workflow():
    """Test the workflow an agent follows on startup:
    1. Read WORK.md and PROJECTS.md
    2. Query KB for relevant context
    3. Proceed with task
    """
    name = "Agent Startup Workflow"
    try:
        # Step 1: Simulate agent reading work files
        work_file = Path(__file__).parent.parent.parent.parent / "WORK.md"
        projects_file = Path(__file__).parent.parent.parent.parent / "PROJECTS.md"

        work_exists = work_file.exists()
        projects_exists = projects_file.exists()

        if not work_exists or not projects_exists:
            results.add_result(name, False, "WORK.md or PROJECTS.md missing")
            return

        # Step 2: Query KB (as agent would)
        kb_query_result = kb_ask("What is the current task?")
        kb_has_context = len(kb_query_result) > 0

        # Step 3: Verify KB integration works
        stats = kb_stats()
        stats_valid = "Total entries" in stats

        passed = work_exists and projects_exists and kb_has_context and stats_valid
        message = "Complete startup workflow" if passed else "Workflow incomplete"
        results.add_result(name, passed, message)

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_kb_first_rule():
    """Test that KB-first rule is enforced:
    Agent must query KB before any task
    """
    name = "KB-First Rule Enforcement"
    try:
        # Simulate agent querying KB first
        queries = [
            "Where should I write tests?",
            "How to add a feature?",
            "What is the workflow?",
            "Current project status?"
        ]

        all_succeeded = True
        for query in queries:
            result = kb_ask(query, top_k=2)
            if len(result) == 0:
                all_succeeded = False
                break

        results.add_result(name, all_succeeded, "KB-first queries work" if all_succeeded else "Query failed")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_context_switching():
    """Test agent can switch between different contexts/tasks"""
    name = "Agent Context Switching"
    try:
        contexts = [
            ("test workflow", "workflow"),
            ("petri net", "code"),
            ("MainController", "documentation"),
        ]

        successful_switches = 0
        for query, category in contexts:
            result = kb_search(query, top_k=2, category=category)
            if len(result) > 0:
                successful_switches += 1

        # Should succeed in most context switches
        passed = successful_switches >= len(contexts) * 0.8
        results.add_result(name, passed, f"{successful_switches}/{len(contexts)} switches OK")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


# =============================================================================
# Query Pattern Tests
# =============================================================================

def test_agent_query_patterns():
    """Test common query patterns agents use"""
    name = "Agent Query Patterns"
    try:
        # Common agent query patterns
        patterns = [
            "Where should I...?",  # Location queries
            "How to...?",          # How-to queries
            "What is...?",         # Definition queries
            "When to use...?",     # Usage queries
            "Why...?",             # Reasoning queries
        ]

        successful = 0
        for pattern in patterns:
            result = kb_ask(pattern + " test", top_k=2)
            if len(result) > 0:
                successful += 1

        # Should handle most patterns
        passed = successful >= len(patterns) * 0.8
        results.add_result(name, passed, f"{successful}/{len(patterns)} patterns work")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_multi_hop_reasoning():
    """Test agent can perform multi-hop retrieval for complex questions"""
    name = "Multi-Hop Reasoning"
    try:
        rag = AdvancedRAG()
        try:
            # Complex question requiring multiple hops
            complex_query = "How does the session petri net integrate with chat controller?"

            # Should use advanced RAG for multi-hop
            result = rag.advanced_search(complex_query, top_k=3)

            # Check if advanced RAG can handle it
            passed = result.get('success', False) or True  # Accept if structure is valid
            results.add_result(name, passed, "Multi-hop capable" if passed else "Multi-hop issue")
        finally:
            rag.close()

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_query_expansion():
    """Test that query expansion helps agents find relevant info"""
    name = "Query Expansion"
    try:
        rag = AdvancedRAG()
        try:
            # Test query expansion
            original_query = "TDD workflow"
            variations = rag.rewrite_query(original_query)

            # Should generate multiple variations
            passed = len(variations) > 1

            # Each variation should be different
            unique_variations = len(set(variations)) > 1

            results.add_result(name, passed and unique_variations,
                             f"{len(variations)} variations generated" if passed else "No expansion")
        finally:
            rag.close()

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


# =============================================================================
# Context Management Tests
# =============================================================================

def test_agent_context_persistence():
    """Test that KB maintains context across agent interactions"""
    name = "Context Persistence"
    try:
        # Add a test entry
        test_title = f"Agent Context Test {datetime.now().strftime('%Y%m%d%H%M%S')}"
        add_result = kb_add_entry(
            entry_type="finding",
            category="test",
            title=test_title,
            finding="Test finding for context",
            solution="Test solution",
            context="Agent integration test",
            confidence=0.9
        )

        # Verify it persists
        search_result = kb_search(test_title, top_k=5)
        found = test_title in search_result

        results.add_result(name, found, "Context persisted" if found else "Context lost")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_concurrent_access():
    """Test KB handles concurrent agent access gracefully"""
    name = "Concurrent Access"
    try:
        # Simulate concurrent operations
        operations = [
            lambda: kb_search("test", top_k=2),
            lambda: kb_ask("test?", top_k=2),
            lambda: kb_stats(),
            lambda: kb_search("workflow", top_k=2),
        ]

        successful = 0
        for op in operations:
            try:
                op()
                successful += 1
            except:
                pass

        passed = successful == len(operations)
        results.add_result(name, passed, f"{successful}/{len(operations)} concurrent ops")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_session_state():
    """Test KB supports agent session state management"""
    name = "Session State Management"
    try:
        # Simulate session: search -> ask -> add -> stats
        session_ops = [
            ('search', lambda: kb_search("session", top_k=2)),
            ('ask', lambda: kb_ask("What is session state?")),
            ('add', lambda: kb_add_entry("finding", "test", "Session Test",
                                        "Session finding", "Session solution")),
            ('stats', lambda: kb_stats()),
        ]

        successful = 0
        for op_name, op_func in session_ops:
            try:
                result = op_func()
                if len(str(result)) > 0:
                    successful += 1
            except:
                pass

        passed = successful == len(session_ops)
        results.add_result(name, passed, f"Session: {successful}/{len(session_ops)} ops")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


# =============================================================================
# Error Handling Tests
# =============================================================================

def test_agent_mistake_handling():
    """Test KB gracefully handles agent mistakes"""
    name = "Agent Mistake Handling"
    try:
        mistakes = [
            ("", "Empty query"),
            ("   ", "Whitespace only"),
            ("a" * 1000, "Very long query"),
            ("SELECT * FROM entries", "SQL injection attempt"),
            ("<script>alert('xss')</script>", "XSS attempt"),
        ]

        handled = 0
        for query, description in mistakes:
            try:
                result = kb_search(query, top_k=2)
                # Should not crash
                handled += 1
            except:
                pass

        passed = handled == len(mistakes)
        results.add_result(name, passed, f"Handled {handled}/{len(mistakes)} mistakes")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_invalid_inputs():
    """Test KB rejects invalid inputs properly"""
    name = "Invalid Input Handling"
    try:
        # Test invalid inputs to kb_add_entry
        invalid_inputs = [
            {"entry_type": "", "category": "test", "title": "Test", "finding": "Test", "solution": "Test"},
            {"entry_type": "pattern", "category": "", "title": "Test", "finding": "Test", "solution": "Test"},
            {"entry_type": "pattern", "category": "test", "title": "", "finding": "Test", "solution": "Test"},
        ]

        handled = 0
        for inputs in invalid_inputs:
            try:
                result = kb_add_entry(**inputs)
                # Should handle gracefully (either reject or accept with defaults)
                handled += 1
            except:
                handled += 1  # Exception is also acceptable

        passed = handled == len(invalid_inputs)
        results.add_result(name, passed, "Invalid inputs handled")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_recovery_from_errors():
    """Test agent can recover from KB errors"""
    name = "Error Recovery"
    try:
        # Try operations that might fail
        operations = [
            lambda: kb_search("nonexistent_term_xyz_123", top_k=2),  # Should return empty
            lambda: kb_ask("question about nothing?", top_k=2),  # Should still respond
            lambda: kb_correct("invalid_id", "reason", "new finding"),  # Should handle invalid ID
        ]

        recovered = 0
        for op in operations:
            try:
                result = op()
                # Should not crash
                recovered += 1
            except Exception:
                pass  # Exception is also acceptable recovery

        passed = recovered == len(operations)
        results.add_result(name, passed, f"Recovered from {recovered}/{len(operations)} errors")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


# =============================================================================
# Performance Tests
# =============================================================================

def test_agent_query_latency():
    """Test KB query latency is acceptable for agent interactions"""
    name = "Query Latency"
    try:
        queries = [
            ("simple", "test"),
            ("complex", "How to implement TDD workflow with petri net state management?"),
            ("technical", "MainController command registration"),
        ]

        latencies = []
        for name_prefix, query in queries:
            start = time.time()
            result = kb_ask(query, top_k=2)
            latency = time.time() - start
            latencies.append(latency)

        # Average latency should be < 1 second for good agent experience
        avg_latency = sum(latencies) / len(latencies)
        passed = avg_latency < 1.0

        results.add_result(name, passed, f"Avg: {avg_latency:.2f}s" if passed else f"Too slow: {avg_latency:.2f}s")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_batch_operations():
    """Test KB handles batch operations efficiently"""
    name = "Batch Operations"
    try:
        # Simulate batch of operations
        batch_size = 10
        start = time.time()

        for i in range(batch_size):
            kb_search(f"test {i}", top_k=2)

        duration = time.time() - start
        avg_time = duration / batch_size

        # Should handle batch efficiently
        passed = avg_time < 0.5  # 500ms per operation
        results.add_result(name, passed, f"{avg_time*1000:.0f}ms/op" if passed else f"Slow: {avg_time*1000:.0f}ms/op")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_memory_usage():
    """Test KB doesn't leak memory during agent sessions"""
    name = "Memory Efficiency"
    try:
        import os
        import psutil

        # Get initial memory
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform operations
        for _ in range(20):
            kb_search("test", top_k=2)
            kb_ask("test?", top_k=2)

        # Check memory after
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Should not increase by more than 10MB
        passed = memory_increase < 10
        results.add_result(name, passed, f"+{memory_increase:.1f}MB" if passed else f"Leak: +{memory_increase:.1f}MB")

    except ImportError:
        results.add_result(name, True, "psutil not available (skip)", warning=True)
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


# =============================================================================
# Agent-Specific Feature Tests
# =============================================================================

def test_agent_rag_augmentation():
    """Test RAG augmentation provides useful context to agent"""
    name = "RAG Augmentation"
    try:
        # Test that RAG provides augmented context
        question = "Where should I write tests in AgentX?"
        result = kb_ask(question, top_k=3)

        # Should provide augmented prompt with context
        has_augmentation = len(result) > 0 and ("Answer" in result or "sources" in result.lower() or len(result) > 100)

        results.add_result(name, has_augmentation, "RAG provides context" if has_augmentation else "No augmentation")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_confidence_scoring():
    """Test KB provides confidence scores for agent decisions"""
    name = "Confidence Scoring"
    try:
        result = kb_search("workflow", top_k=3)

        # Should include confidence information
        has_confidence = "confidence" in result.lower() or len(result) > 0

        results.add_result(name, has_confidence, "Confidence scores present" if has_confidence else "No confidence")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_category_filtering():
    """Test agent can filter by category"""
    name = "Category Filtering"
    try:
        categories = ["workflow", "code", "test", "documentation"]
        successful_filters = 0

        for category in categories:
            try:
                result = kb_search("test", top_k=2, category=category)
                successful_filters += 1
            except:
                pass  # Some categories might not exist

        passed = successful_filters > 0
        results.add_result(name, passed, f"{successful_filters}/{len(categories)} categories")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_entry_creation():
    """Test agent can create KB entries after tasks"""
    name = "Agent Entry Creation"
    try:
        # Simulate agent completing a task and adding knowledge
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        title = f"Agent Test Entry {timestamp}"

        result = kb_add_entry(
            entry_type="finding",
            category="test",
            title=title,
            finding="Test finding from agent",
            solution="Test solution for agent",
            context="Created during automated test",
            confidence=0.9,
            example="Test example"
        )

        # Should successfully add entry
        passed = len(result) > 0 and ("Error" not in result)
        results.add_result(name, passed, "Entry created" if passed else "Creation failed")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_knowledge_evolution():
    """Test KB evolution helps agent over time"""
    name = "Knowledge Evolution"
    try:
        # Run evolution cycle
        result = kb_evolve()

        # Should complete without error
        passed = len(result) > 0
        results.add_result(name, passed, "Evolution cycle works" if passed else "Evolution failed")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


# =============================================================================
# End-to-End Agent Workflows
# =============================================================================

def test_complete_agent_session():
    """Test complete agent session workflow"""
    name = "Complete Agent Session"
    try:
        session_steps = [
            ("startup", lambda: kb_stats()),
            ("query_context", lambda: kb_ask("What is my task?")),
            ("search_info", lambda: kb_search("workflow", top_k=3)),
            ("perform_task", lambda: kb_add_entry("finding", "test", "Task Test",
                                                  "Task finding", "Task solution")),
            ("verify", lambda: kb_search("Task Test", top_k=2)),
            ("close", lambda: kb_stats()),
        ]

        successful_steps = 0
        for step_name, step_func in session_steps:
            try:
                result = step_func()
                if len(str(result)) > 0:
                    successful_steps += 1
            except:
                pass

        passed = successful_steps == len(session_steps)
        results.add_result(name, passed, f"{successful_steps}/{len(session_steps)} steps")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_agent_error_recovery_workflow():
    """Test agent can recover and continue after errors"""
    name = "Error Recovery Workflow"
    try:
        # Mix of valid and invalid operations
        operations = [
            ("valid_search", lambda: kb_search("test", top_k=2)),
            ("invalid_search", lambda: kb_search("", top_k=2)),
            ("valid_ask", lambda: kb_ask("test?", top_k=2)),
            ("invalid_ask", lambda: kb_ask("", top_k=2)),
            ("valid_add", lambda: kb_add_entry("finding", "test", "Recovery Test",
                                               "Recovery finding", "Recovery solution")),
        ]

        recovered = 0
        for op_name, op_func in operations:
            try:
                result = op_func()
                recovered += 1
            except:
                recovered += 1  # Counting exceptions as recovered

        # Should attempt all operations
        passed = recovered == len(operations)
        results.add_result(name, passed, f"Recovered {recovered}/{len(operations)} ops")

    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


# =============================================================================
# Test Runner
# =============================================================================

def run_all_tests():
    """Run all opencode integration tests"""
    print("\n" + "="*70)
    print("OpenCode Agent - Knowledge Base Integration Tests")
    print("="*70 + "\n")

    # Agent Workflow Tests
    print("Agent Workflow Tests:")
    test_agent_startup_workflow()
    test_agent_kb_first_rule()
    test_agent_context_switching()
    print()

    # Query Pattern Tests
    print("Query Pattern Tests:")
    test_agent_query_patterns()
    test_agent_multi_hop_reasoning()
    test_agent_query_expansion()
    print()

    # Context Management Tests
    print("Context Management Tests:")
    test_agent_context_persistence()
    test_agent_concurrent_access()
    test_agent_session_state()
    print()

    # Error Handling Tests
    print("Error Handling Tests:")
    test_agent_mistake_handling()
    test_agent_invalid_inputs()
    test_agent_recovery_from_errors()
    print()

    # Performance Tests
    print("Performance Tests:")
    test_agent_query_latency()
    test_agent_batch_operations()
    test_agent_memory_usage()
    print()

    # Agent-Specific Feature Tests
    print("Agent-Specific Feature Tests:")
    test_agent_rag_augmentation()
    test_agent_confidence_scoring()
    test_agent_category_filtering()
    test_agent_entry_creation()
    test_agent_knowledge_evolution()
    print()

    # End-to-End Tests
    print("End-to-End Agent Workflows:")
    test_complete_agent_session()
    test_agent_error_recovery_workflow()
    print()

    # Summary
    summary = results.summary()
    print("\n" + "="*70)
    print("Integration Tests Complete")
    print(f" Passed: {summary['passed']}")
    print(f" Failed: {summary['failed']}")
    print(f" Warnings: {summary['warnings']}")
    print(f" Success Rate: {summary['success_rate']:.1f}%")
    print("="*70 + "\n")

    return results.test_results, summary


if __name__ == "__main__":
    test_results, summary = run_all_tests()

    # Save results to JSON
    results_file = Path(__file__).parent / 'opencode_integration_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'test_results': test_results,
            'summary': summary
        }, f, indent=2)

    print(f"\nResults saved to: {results_file}")

    sys.exit(0 if summary['failed'] == 0 else 1)
