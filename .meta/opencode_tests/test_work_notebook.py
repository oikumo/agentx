#!/usr/bin/env python3
"""
Test script to validate WORK notebook functionality.

This test verifies:
1. WORK.md file exists
2. WORK.md has correct structure
3. WORK.md can be read and displayed
4. WORK.md can be updated by agent
"""

import os
import sys
from pathlib import Path

def test_work_file_exists():
    """Test that .meta/WORK.md exists"""
    work_path = Path(".meta/WORK.md")
    assert work_path.exists(), f"WORK.md not found at {work_path}"
    print("✓ WORK.md file exists")
    return True

def test_work_file_structure():
    """Test that WORK.md has correct structure"""
    work_path = Path(".meta/WORK.md")
    content = work_path.read_text()
    
    required_sections = [
        "# Current Work",
        "**Purpose**",
        "**Updated by**",
        "**Status**",
        "## Current Task"
    ]
    
    for section in required_sections:
        assert section in content, f"Missing required section: {section}"
    
    print("✓ WORK.md has correct structure")
    return True

def test_work_file_readable():
    """Test that WORK.md can be read"""
    work_path = Path(".meta/WORK.md")
    content = work_path.read_text()
    assert len(content) > 0, "WORK.md is empty"
    print(f"✓ WORK.md is readable ({len(content)} bytes)")
    return True

def test_work_file_updatable():
    """Test that WORK.md can be updated"""
    work_path = Path(".meta/WORK.md")
    
    # Save original content
    original = work_path.read_text()
    
    try:
        # Test update
        test_content = """# Current Work Notebook

> **Purpose**: Quick reminder of what you're working on  
> **Updated by**: Agent (automatically when you start a new task)  
> **Shown**: Once at the start of each session

---

## Current Task

**Status**: Test in progress

---

*This file is automatically updated by your AI assistant when you start working on something new. It serves as a simple reminder, not a task tracker.*
"""
        work_path.write_text(test_content)
        
        # Verify update
        updated = work_path.read_text()
        assert "Test in progress" in updated, "Failed to update WORK.md"
        print("✓ WORK.md can be updated")
        
    finally:
        # Restore original
        work_path.write_text(original)
    
    return True

def test_meta_harness_references_work():
    """Test that META_HARNESS.md references WORK.md"""
    meta_path = Path("META_HARNESS.md")
    if meta_path.exists():
        content = meta_path.read_text()
        assert "WORK.md" in content or "Work notebook" in content, \
            "META_HARNESS.md should reference WORK.md"
        print("✓ META_HARNESS.md references WORK.md")
    return True

def test_agents_md_references_work():
    """Test that AGENTS.md references WORK.md"""
    agents_path = Path("AGENTS.md")
    if agents_path.exists():
        content = agents_path.read_text()
        assert "WORK.md" in content or "Work Notebook" in content, \
            "AGENTS.md should reference WORK.md"
        print("✓ AGENTS.md references WORK.md")
    return True

def main():
    """Run all tests"""
    tests = [
        ("WORK.md exists", test_work_file_exists),
        ("WORK.md structure", test_work_file_structure),
        ("WORK.md readable", test_work_file_readable),
        ("WORK.md updatable", test_work_file_updatable),
        ("META_HARNESS.md reference", test_meta_harness_references_work),
        ("AGENTS.md reference", test_agents_md_references_work),
    ]
    
    print("=" * 60)
    print("WORK Notebook Test Suite")
    print("=" * 60)
    print()
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {name}: Unexpected error - {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
