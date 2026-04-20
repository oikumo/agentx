#!/usr/bin/env python3
"""
Test script for Knowledge Base MCP tools.
Run this to verify all tools are working correctly.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
package_dir = Path(__file__).parent
sys.path.insert(0, str(package_dir))

# Import from rag_tool module
from rag_tool import (
    rag_search,
    rag_ask,
    rag_add_entry,
    rag_correct,
    rag_evolve,
    rag_stats
)

def test_search():
    """Test kb_search."""
    print("1. Testing kb_search...")
    result = rag_search("TDD", top_k=3)
    assert result["success"], f"Search failed: {result}"
    print(f"   ✓ Found {result['count']} entries")
    return True

def test_ask():
    """Test kb_ask."""
    print("2. Testing kb_ask...")
    result = rag_ask("Where should I write tests?")
    assert result["success"], f"Ask failed: {result}"
    assert "augmented_prompt" in result
    print(f"   ✓ Retrieved {result['context_count']} context entries")
    return True

def test_add_entry():
    """Test kb_add_entry."""
    print("3. Testing kb_add_entry...")
    result = rag_add_entry(
        entry_type="pattern",
        category="workflow",
        title="Test Pattern for Validation",
        finding="This is a test finding",
        solution="This is a test solution",
        context="Testing the KB tools",
        confidence=0.95
    )
    assert result["success"], f"Add entry failed: {result}"
    entry_id = result.get("entry_id")
    print(f"   ✓ Added entry: {entry_id}")
    return entry_id

def test_correct_entry(entry_id):
    """Test kb_correct."""
    print(f"4. Testing kb_correct on {entry_id}...")
    result = rag_correct(
        entry_id=entry_id,
        reason="Testing correction mechanism",
        new_finding="Updated test finding"
    )
    assert result["success"], f"Correct failed: {result}"
    print(f"   ✓ Corrected entry, confidence: {result['old_confidence']:.2f} → {result['new_confidence']:.2f}")
    return True

def test_evolve():
    """Test kb_evolve."""
    print("5. Testing kb_evolve...")
    result = rag_evolve()
    assert result["success"], f"Evolve failed: {result}"
    print(f"   ✓ {result['message']}")
    return True

def test_stats():
    """Test kb_stats."""
    print("6. Testing kb_stats...")
    result = rag_stats()
    assert result["success"], f"Stats failed: {result}"
    print(f"   ✓ Total entries: {result['total_entries']}")
    print(f"   ✓ By type: {result['by_type']}")
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Knowledge Base MCP Tools - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_search,
        test_ask,
        test_add_entry,
        lambda: test_correct_entry(test_add_entry()),
        test_evolve,
        test_stats,
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(tests, 1):
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ✗ Test {i} failed: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
