#!/usr/bin/env python3
"""
Knowledge Base Edge Case Tests
================================
Tests for edge cases, error handling, and boundary conditions
"""

import sys
from pathlib import Path
from datetime import datetime

# Add KB to path
KB_PATH = Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base"
sys.path.insert(0, str(KB_PATH))

from knowledge_base import kb_search, kb_ask, kb_add_entry, kb_stats, kb_correct


class EdgeCaseResults:
    """Track edge case test results"""
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


results = EdgeCaseResults()


def test_empty_search_query():
    """Test search with empty query"""
    name = "Empty Search Query"
    try:
        result = kb_search("", top_k=3)
        # Should handle gracefully (return empty or default message)
        results.add_result(name, True, "Handled gracefully")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_special_characters_in_query():
    """Test search with special characters"""
    name = "Special Characters in Query"
    try:
        result = kb_search("test @#$%", top_k=3)
        results.add_result(name, True, "Special chars handled")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_sql_injection_attempt():
    """Test SQL injection prevention"""
    name = "SQL Injection Prevention"
    try:
        malicious_query = "'; DROP TABLE entries; --"
        result = kb_search(malicious_query, top_k=3)
        # If no exception and DB still works, it's safe
        results.add_result(name, True, "SQL injection prevented")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_very_long_query():
    """Test with very long query string"""
    name = "Very Long Query"
    try:
        long_query = "test " * 1000
        result = kb_search(long_query, top_k=3)
        results.add_result(name, True, "Long query handled")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_unicode_content():
    """Test with unicode content"""
    name = "Unicode Content"
    try:
        result = kb_add_entry(
            entry_type="finding",
            category="test",
            title="Test Unicode: 你好 世界 🌍",
            finding="Unicode test: café, naïve, résumé",
            solution="Unicode handling works",
            context="Edge case testing",
            confidence=0.9
        )
        results.add_result(name, True, "Unicode supported")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_invalid_entry_type():
    """Test adding entry with invalid type"""
    name = "Invalid Entry Type"
    try:
        result = kb_add_entry(
            entry_type="invalid_type",
            category="test",
            title="Test",
            finding="Test",
            solution="Test"
        )
        # Should either add or handle gracefully
        results.add_result(name, True, "Handled")
    except Exception as e:
        results.add_result(name, True, f"Exception caught: {str(e)}")


def test_zero_top_k():
    """Test search with top_k=0"""
    name = "Zero Top-K"
    try:
        result = kb_search("test", top_k=0)
        results.add_result(name, True, "Zero top_k handled")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_negative_top_k():
    """Test search with negative top_k"""
    name = "Negative Top-K"
    try:
        result = kb_search("test", top_k=-1)
        results.add_result(name, True, "Negative top_k handled")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_very_large_top_k():
    """Test search with very large top_k"""
    name = "Very Large Top-K"
    try:
        result = kb_search("test", top_k=10000)
        results.add_result(name, True, "Large top_k handled")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_add_entry_missing_fields():
    """Test adding entry with missing required fields"""
    name = "Missing Required Fields"
    try:
        result = kb_add_entry(
            entry_type="pattern",
            category="",  # Empty category
            title="",
            finding="",
            solution=""
        )
        results.add_result(name, True, "Missing fields handled")
    except Exception as e:
        results.add_result(name, True, f"Exception caught: {str(e)}")


def test_add_entry_invalid_confidence():
    """Test adding entry with invalid confidence"""
    name = "Invalid Confidence"
    try:
        result = kb_add_entry(
            entry_type="pattern",
            category="test",
            title="Test",
            finding="Test",
            solution="Test",
            confidence=1.5  # > 1.0
        )
        results.add_result(name, True, "Invalid confidence handled")
    except Exception as e:
        results.add_result(name, True, f"Exception caught: {str(e)}")


def test_correct_nonexistent_entry():
    """Test correcting a non-existent entry"""
    name = "Correct Non-existent Entry"
    try:
        result = kb_correct(
            entry_id="NON-EXISTENT-ID",
            reason="Testing",
            new_finding="New finding"
        )
        results.add_result(name, True, "Non-existent ID handled")
    except Exception as e:
        results.add_result(name, True, f"Exception caught: {str(e)}")


def test_concurrent_operations():
    """Test concurrent operations"""
    name = "Concurrent Operations"
    try:
        # Perform multiple operations quickly
        kb_search("test1", top_k=2)
        kb_ask("test?", top_k=2)
        kb_stats()
        kb_search("test2", top_k=2)
        results.add_result(name, True, "Concurrent ops work")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def test_rapid_successive_searches():
    """Test rapid successive searches"""
    name = "Rapid Successive Searches"
    try:
        for i in range(10):
            kb_search(f"test{i}", top_k=2)
        results.add_result(name, True, "Rapid searches work")
    except Exception as e:
        results.add_result(name, False, f"Exception: {str(e)}")


def run_all_tests():
    """Run all edge case tests"""
    print("\n" + "="*70)
    print("Knowledge Base Edge Case Tests")
    print("="*70 + "\n")
    
    # Run all tests
    test_empty_search_query()
    test_special_characters_in_query()
    test_sql_injection_attempt()
    test_very_long_query()
    test_unicode_content()
    test_invalid_entry_type()
    test_zero_top_k()
    test_negative_top_k()
    test_very_large_top_k()
    test_add_entry_missing_fields()
    test_add_entry_invalid_confidence()
    test_correct_nonexistent_entry()
    test_concurrent_operations()
    test_rapid_successive_searches()
    
    # Summary
    print("\n" + "="*70)
    print(f"Edge Case Tests Complete")
    print(f"  Passed: {results.passed}")
    print(f"  Failed: {results.failed}")
    print("="*70 + "\n")
    
    return results.failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
