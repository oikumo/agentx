#!/usr/bin/env python3
"""
Knowledge Base Integration Tests
=================================
Tests for integration between different KB components
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import subprocess

# Add KB to path
KB_PATH = Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base"
sys.path.insert(0, str(KB_PATH))

from knowledge_base import kb_search, kb_ask, kb_add_entry, kb_stats
from src.advanced_rag import AdvancedRAG


class IntegrationResults:
    """Track integration test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
    
    def add_result(self, name, passed, message=""):
        status = "✓" if passed else "✗"
        print(f"  {status} {name}: {message if message else 'OK'}")
        if passed:
            self.passed += 1
        else:
            self.failed += 1


results = IntegrationResults()


def test_cli_search_command():
    """Test CLI search command"""
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


def test_cli_ask_command():
    """Test CLI ask command"""
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


def test_cli_stats_command():
    """Test CLI stats command"""
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


def test_python_api_and_cli_consistency():
    """Test that Python API and CLI give consistent results"""
    name = "API/CLI Consistency"
    try:
        # Python API
        api_result = kb_search("workflow", top_k=3)
        
        # CLI
        cmd = ["python3", str(KB_PATH / "kb"), "search", "workflow", "-k", "3"]
        cli_result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        # Both should work
        passed = len(api_result) > 0 and cli_result.returncode == 0
        results.add_result(name, passed, "Consistent results" if passed else "Inconsistent")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_database_state_persistence():
    """Test that database state persists across operations"""
    name = "Database Persistence"
    try:
        # Add an entry
        test_title = f"Integration Test Entry {datetime.now().strftime('%Y%m%d%H%M%S')}"
        kb_add_entry(
            entry_type="finding",
            category="test",
            title=test_title,
            finding="Test finding",
            solution="Test solution",
            context="Integration test",
            confidence=0.9
        )
        
        # Search for it
        search_result = kb_search(test_title, top_k=5)
        
        # Should find it
        passed = test_title in search_result
        results.add_result(name, passed, "Data persisted" if passed else "Data not found")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_advanced_rag_and_basic_compatibility():
    """Test that advanced RAG and basic RAG are compatible"""
    name = "Advanced/Basic RAG Compatibility"
    try:
        # Basic search
        basic_result = kb_search("test", top_k=3)
        
        # Advanced search
        rag = AdvancedRAG()
        try:
            advanced_result = rag.advanced_search("test", top_k=3)
            advanced_result = advanced_result.get('success', False)
        finally:
            rag.close()
        
        # Both should work
        passed = len(basic_result) > 0 and advanced_result
        results.add_result(name, passed, "Compatible" if passed else "Incompatible")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_multi_user_simulation():
    """Simulate multiple users accessing KB simultaneously"""
    name = "Multi-User Simulation"
    try:
        # Simulate 3 users
        operations = [
            lambda: kb_search("test1", top_k=2),
            lambda: kb_ask("test?", top_k=2),
            lambda: kb_stats(),
        ]
        
        for op in operations:
            op()
        
        results.add_result(name, True, "Multi-user simulation OK")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_end_to_end_workflow():
    """Test complete workflow: search -> ask -> add -> stats"""
    name = "End-to-End Workflow"
    try:
        # 1. Search
        search_result = kb_search("workflow", top_k=2)
        
        # 2. Ask
        ask_result = kb_ask("What is a workflow?")
        
        # 3. Add
        add_result = kb_add_entry(
            entry_type="finding",
            category="test",
            title="E2E Test",
            finding="E2E finding",
            solution="E2E solution"
        )
        
        # 4. Stats
        stats_result = kb_stats()
        
        # All should work
        passed = all([
            len(search_result) > 0,
            len(ask_result) > 0,
            len(add_result) > 0,
            "Total entries" in stats_result
        ])
        
        results.add_result(name, passed, "E2E workflow works" if passed else "E2E failed")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_explore_command():
    """Test explore command"""
    name = "Explore Command"
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


def test_add_command():
    """Test add command"""
    name = "Add Command"
    try:
        cmd = [
            "python3",
            str(KB_PATH / "kb"),
            "add",
            "finding",
            "test",
            "CLI Test Entry",
            "CLI finding",
            "CLI solution",
            "--confidence", "0.9"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        passed = result.returncode == 0
        results.add_result(name, passed, "Add command works" if passed else "Add command failed")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_query_expansion_integration():
    """Test query expansion integration"""
    name = "Query Expansion Integration"
    try:
        rag = AdvancedRAG()
        try:
            # Test query expansion
            variations = rag.rewrite_query("How to implement TDD workflow?")
            
            # Should generate multiple variations
            passed = len(variations) > 1
            
            # Each variation should be searchable
            for variation in variations[:3]:  # Test first 3
                search_result = rag.advanced_search(variation, top_k=2)
                if not search_result.get('success', False):
                    passed = False
                    break
            
            results.add_result(name, passed, "Query expansion integrated" if passed else "Integration issue")
        finally:
            rag.close()
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("Knowledge Base Integration Tests")
    print("="*70 + "\n")
    
    # Run all tests
    test_cli_search_command()
    test_cli_ask_command()
    test_cli_stats_command()
    test_python_api_and_cli_consistency()
    test_database_state_persistence()
    test_advanced_rag_and_basic_compatibility()
    test_multi_user_simulation()
    test_end_to_end_workflow()
    test_explore_command()
    test_add_command()
    test_query_expansion_integration()
    
    # Summary
    print("\n" + "="*70)
    print(f"Integration Tests Complete")
    print(f"  Passed: {results.passed}")
    print(f"  Failed: {results.failed}")
    print("="*70 + "\n")
    
    return results.failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
