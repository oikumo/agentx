#!/usr/bin/env python3
"""
Knowledge Base Performance Tests
=================================
Tests for KB performance and stress testing
"""

import sys
import time
from pathlib import Path
from datetime import datetime
import statistics

# Add KB to path
KB_PATH = Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base"
sys.path.insert(0, str(KB_PATH))

from knowledge_base import kb_search, kb_ask, kb_stats
from src.advanced_rag import AdvancedRAG


class PerformanceResults:
    """Track performance results"""
    def __init__(self):
        self.tests = []
    
    def add_result(self, name, metric, value, threshold, passed):
        status = "✓" if passed else "✗"
        print(f"  {status} {name}: {value:.3f}s (threshold: {threshold:.3f}s)")
        self.tests.append({
            'name': name,
            'metric': metric,
            'value': value,
            'threshold': threshold,
            'passed': passed
        })


results = PerformanceResults()


def test_search_performance():
    """Test search performance"""
    name = "Search Performance (avg)"
    queries = ["MainController", "workflow", "TDD", "Petri net", "Session"]
    times = []
    
    for query in queries:
        start = time.time()
        kb_search(query, top_k=5)
        times.append(time.time() - start)
    
    avg_time = statistics.mean(times)
    threshold = 0.1  # 100ms
    passed = avg_time < threshold
    results.add_result(name, "avg_time", avg_time, threshold, passed)


def test_ask_performance():
    """Test ask performance"""
    name = "Ask Performance (avg)"
    questions = [
        "What is MainController?",
        "How do I use TDD?",
        "Where is the sandbox?"
    ]
    times = []
    
    for question in questions:
        start = time.time()
        kb_ask(question, top_k=3)
        times.append(time.time() - start)
    
    avg_time = statistics.mean(times)
    threshold = 0.2  # 200ms
    passed = avg_time < threshold
    results.add_result(name, "avg_time", avg_time, threshold, passed)


def test_stats_performance():
    """Test stats performance"""
    name = "Stats Performance"
    
    times = []
    for _ in range(5):
        start = time.time()
        kb_stats()
        times.append(time.time() - start)
    
    avg_time = statistics.mean(times)
    threshold = 0.5  # 500ms
    passed = avg_time < threshold
    results.add_result(name, "avg_time", avg_time, threshold, passed)


def test_concurrent_searches():
    """Test multiple concurrent searches"""
    name = "Concurrent Searches (10)"
    
    queries = ["test"] * 10
    start = time.time()
    for query in queries:
        kb_search(query, top_k=3)
    total_time = time.time() - start
    
    avg_time = total_time / 10
    threshold = 0.15  # 150ms per search
    passed = avg_time < threshold
    results.add_result(name, "avg_time", avg_time, threshold, passed)


def test_database_connection_pooling():
    """Test database connection reuse"""
    name = "DB Connection Reuse"
    
    start = time.time()
    rag = AdvancedRAG()
    
    # Perform multiple operations
    for _ in range(10):
        rag.advanced_search("test", top_k=2)
    
    total_time = time.time() - start
    avg_time = total_time / 10
    
    rag.close()
    
    threshold = 0.1  # 100ms per search with connection reuse
    passed = avg_time < threshold
    results.add_result(name, "avg_time", avg_time, threshold, passed)


def test_large_result_set():
    """Test performance with large result sets"""
    name = "Large Result Set (top_k=50)"
    
    start = time.time()
    result = kb_search("pattern", top_k=50)
    elapsed = time.time() - start
    
    threshold = 0.5  # 500ms
    passed = elapsed < threshold
    results.add_result(name, "elapsed_time", elapsed, threshold, passed)


def test_query_expansion_performance():
    """Test query expansion performance"""
    name = "Query Expansion"
    
    rag = AdvancedRAG()
    try:
        start = time.time()
        variations = rag.rewrite_query("complex query with multiple terms")
        elapsed = time.time() - start
        
        threshold = 0.05  # 50ms
        passed = elapsed < threshold
        results.add_result(name, "elapsed_time", elapsed, threshold, passed)
    finally:
        rag.close()


def test_memory_usage():
    """Test memory usage (basic check)"""
    name = "Memory Usage Check"
    
    import tracemalloc
    tracemalloc.start()
    
    rag = AdvancedRAG()
    rag.advanced_search("test", top_k=5)
    rag.ask("test?", top_k=3)
    rag.close()
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Peak memory should be under 50MB
    peak_mb = peak / 1024 / 1024
    threshold_mb = 50
    passed = peak_mb < threshold_mb
    results.add_result(name, "peak_memory_mb", peak_mb, threshold_mb, passed)


def run_all_tests():
    """Run all performance tests"""
    print("\n" + "="*70)
    print("Knowledge Base Performance Tests")
    print("="*70 + "\n")
    
    start_time = time.time()
    
    # Run all tests
    test_search_performance()
    test_ask_performance()
    test_stats_performance()
    test_concurrent_searches()
    test_database_connection_pooling()
    test_large_result_set()
    test_query_expansion_performance()
    test_memory_usage()
    
    end_time = time.time()
    
    # Summary
    passed = sum(1 for t in results.tests if t['passed'])
    total = len(results.tests)
    
    print("\n" + "="*70)
    print(f"Performance Tests Complete")
    print(f"  Passed: {passed}/{total}")
    print(f"  Time:   {end_time - start_time:.2f}s")
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
