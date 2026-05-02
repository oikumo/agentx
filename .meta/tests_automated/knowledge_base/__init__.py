# Knowledge Base Automated Tests Package
"""
Automated test suite for Meta Harness Knowledge Base.

This package contains comprehensive tests for:
- Core functionality (search, ask, add, stats)
- Performance (speed, memory, concurrency)
- Edge cases (error handling, boundary conditions)
- Integration (CLI, API, database)

Usage:
    # Run all tests
    ./run_all_tests.sh
    
    # Run specific test suite
    python test_kb_functionality.py
    python test_kb_performance.py
    python test_kb_edge_cases.py
    python test_kb_integration.py

Test Structure:
    - run_all_tests.sh: Main test runner
    - test_kb_functionality.py: Core functionality tests
    - test_kb_performance.py: Performance and stress tests
    - test_kb_edge_cases.py: Edge case and error handling tests
    - test_kb_integration.py: Integration tests
    - README.md: Documentation

Results:
    - Console output with colors
    - JSON results file (test_results.json)
    - Log file (test_run.log)
"""

__version__ = "1.0.0"
__author__ = "Meta Harness"
__date__ = "2026-05-02"
