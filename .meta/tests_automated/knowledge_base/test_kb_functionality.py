#!/usr/bin/env python3
"""
Knowledge Base Functionality Tests
===================================
Comprehensive tests for KB core functionality
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import time

# Add KB to path
KB_PATH = Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base"
sys.path.insert(0, str(KB_PATH))

from knowledge_base import kb_search, kb_ask, kb_add_entry, kb_stats, kb_correct, kb_evolve
from src.advanced_rag import AdvancedRAG


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_result(self, name, passed, message=""):
        self.tests.append({
            'name': name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        if passed:
            self.passed += 1
            print(f"  ✓ {name}")
        else:
            self.failed += 1
            print(f"  ✗ {name}: {message}")


results = TestResults()


def test_search_basic():
    """Test basic search functionality"""
    name = "Basic Search"
    try:
        result = kb_search("MainController", top_k=3)
        passed = "MainController" in result or len(result) > 0
        results.add_result(name, passed, "Search returned results" if passed else "No results")
    except Exception as e:
        results.add_result(name, False, str(e))


def test_search_with_category():
    """Test search with category filter"""
    name = "Search with Category"
    try:
        result = kb_search("workflow", top_k=5, category="workflow")
        passed = len(result) > 0
        results.add_result(name, passed, "Category filter works" if passed else "No results")
    except Exception as e:
        results.add_result(name, False, str(e))


def test_search_empty_query():
    """Test search with empty query"""
    name = "Search Empty Query"
    try:
        result = kb_search("", top_k=3)
        # Should return some results or handle gracefully
        passed = True  # If no exception, it's OK
        results.add_result(name, passed, "Handled gracefully")
    except Exception as e:
        results.add_result(name, False, str(e))


def test_ask_question():
    """Test ask functionality"""
    name = "Ask Question"
    try:
        result = kb_ask("What is the MainController?")
        passed = len(result) > 0 and ("Answer" in result or "sources" in result.lower())
        results.add_result(name, passed, "Got answer" if passed else "No answer")
    except Exception as e:
        results.add_result(name, False, str(e))


def test_ask_complex_question():
    """Test ask with complex question"""
    name = "Ask Complex Question"
    try:
        result = kb_ask("How do I implement TDD in the sandbox?")
        passed = len(result) > 0
        results.add_result(name, passed, "Got comprehensive answer" if passed else "No answer")
    except Exception as e:
        results.add_result(name, False, str(e))


def test_add_entry():
    """Test adding new entry"""
    name = "Add Entry"
    try:
        result = kb_add_entry(
            entry_type="finding",
            category="test",
            title="Test Entry for Automated Testing",
            finding="This is a test finding",
            solution="This is a test solution",
            context="Automated test suite",
            confidence=0.9,
            example="Test example"
        )
        passed = len(result) > 0
        results.add_result(name, passed, "Entry added" if passed else "Failed to add")
    except Exception as e:
        results.add_result(name, False, str(e))


def test_stats():
    """Test statistics functionality"""
    name = "Get Statistics"
    try:
        result = kb_stats()
        passed = "Total entries" in result
        results.add_result(name, passed, "Stats retrieved" if passed else "No stats")
    except Exception as e:
        results.add_result(name, False, str(e))


def test_explore():
    """Test explore functionality"""
    name = "Explore Categories"
    try:
        rag = AdvancedRAG()
        try:
            cursor = rag.conn.cursor()
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM entries
                WHERE is_deprecated = 0
                GROUP BY category
            """)
            results_data = cursor.fetchall()
            passed = len(results_data) > 0
            results.add_result(name, passed, f"Found {len(results_data)} categories" if passed else "No categories")
        finally:
            rag.close()
    except Exception as e:
        results.add_result(name, False, str(e))


def test_advanced_rag_search():
    """Test advanced RAG search"""
    name = "Advanced RAG Search"
    try:
        rag = AdvancedRAG()
        try:
            result = rag.advanced_search("workflow", top_k=3)
            passed = result.get('success', False)
            results.add_result(name, passed, "Advanced search works" if passed else "Search failed")
        finally:
            rag.close()
    except Exception as e:
        results.add_result(name, False, str(e))


def test_advanced_rag_ask():
    """Test advanced RAG ask"""
    name = "Advanced RAG Ask"
    try:
        rag = AdvancedRAG()
        try:
            result = rag.ask("What is TDD?", top_k=3, synthesize=True)
            passed = result.get('success', False)
            results.add_result(name, passed, "Advanced ask works" if passed else "Ask failed")
        finally:
            rag.close()
    except Exception as e:
        results.add_result(name, False, str(e))


def test_query_expansion():
    """Test query expansion feature"""
    name = "Query Expansion"
    try:
        rag = AdvancedRAG()
        try:
            variations = rag.rewrite_query("How to implement TDD workflow?")
            passed = len(variations) > 1
            results.add_result(name, passed, f"Generated {len(variations)} variations" if passed else "No variations")
        finally:
            rag.close()
    except Exception as e:
        results.add_result(name, False, str(e))


def test_multi_hop_retrieval():
    """Test multi-hop retrieval"""
    name = "Multi-Hop Retrieval"
    try:
        rag = AdvancedRAG()
        try:
            results_data = rag.multi_hop_retrieval("TDD workflow", max_hops=2)
            passed = True  # If no exception, it works
            results.add_result(name, passed, "Multi-hop works")
        finally:
            rag.close()
    except Exception as e:
        results.add_result(name, False, str(e))


def run_all_tests():
    """Run all functionality tests"""
    print("\n" + "="*70)
    print("Knowledge Base Functionality Tests")
    print("="*70 + "\n")
    
    start_time = time.time()
    
    # Run all tests
    test_search_basic()
    test_search_with_category()
    test_search_empty_query()
    test_ask_question()
    test_ask_complex_question()
    test_add_entry()
    test_stats()
    test_explore()
    test_advanced_rag_search()
    test_advanced_rag_ask()
    test_query_expansion()
    test_multi_hop_retrieval()
    
    end_time = time.time()
    
    # Summary
    print("\n" + "="*70)
    print(f"Functionality Tests Complete")
    print(f"  Passed: {results.passed}")
    print(f"  Failed: {results.failed}")
    print(f"  Time:   {end_time - start_time:.2f}s")
    print("="*70 + "\n")
    
    return results.failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
