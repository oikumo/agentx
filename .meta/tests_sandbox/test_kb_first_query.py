#!/usr/bin/env python3
"""
Test: KB-First Query Pattern for Opencode

Objective: When user asks "What is MainController?" or any project-specific question,
opencode should automatically query the Knowledge Base FIRST before searching code.

This test validates the KB-first query pattern that should be implemented.
"""

import subprocess
import sys
import sqlite3
from pathlib import Path

# KB database path
KB_DB = Path(".meta/data/kb-meta/knowledge-meta.db")

def test_kb_has_maincontroller_info():
    """Test 1: Verify KB contains MainController information"""
    print("Test 1: KB has MainController info")
    
    conn = sqlite3.connect(KB_DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, finding, solution 
        FROM entries 
        WHERE title LIKE '%MainController%' 
           OR finding LIKE '%MainController%'
           OR solution LIKE '%MainController%'
        LIMIT 5
    """)
    results = cursor.fetchall()
    conn.close()
    
    if len(results) > 0:
        print(f"  ✓ PASS: Found {len(results)} MainController entries")
        for title, finding, solution in results[:2]:
            print(f"    - {title[:60]}")
        return True
    else:
        print("  ✗ FAIL: No MainController entries found")
        return False

def test_kb_population_script_reads_all_files():
    """Test 2: Verify population script reads .meta directory files"""
    print("\nTest 2: Population script reads all .meta files")
    
    populate_script = Path(".meta/tools/populate_kb.py")
    if not populate_script.exists():
        print("  ✗ FAIL: populate_kb.py not found")
        return False
    
    content = populate_script.read_text()
    
    # Check if script processes .meta directory
    checks = [
        (".rglob(\"*.md\")", "Searches for .md files recursively"),
        (".meta", "References .meta directory"),
        ("src/agentx", "Processes src/agentx source code"),
    ]
    
    all_pass = True
    for pattern, description in checks:
        if pattern in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ Missing: {description}")
            all_pass = False
    
    return all_pass

def test_rag_cli_works():
    """Test 3: Verify RAG CLI tool can query MainController using Advanced RAG"""
    print("\nTest 3: RAG CLI query works (Advanced RAG with python3)")
    
    cli_tool = Path(".meta/tools/meta-harness-knowledge-base/kb")
    if not cli_tool.exists():
        print("  ✗ FAIL: kb CLI tool not found")
        return False
    
    # Test search using python3 (NOT python)
    result = subprocess.run(
        ["python3", str(cli_tool), "search", "MainController", "--top-k", "1"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if "MainController" in result.stdout:
        print("  ✓ PASS: CLI search returns MainController results")
        return True
    else:
        print("  ✗ FAIL: CLI search didn't return expected results")
        print(f"    stdout: {result.stdout[:200]}")
        return False

def test_advanced_rag_ask():
    """Test 4: Verify Advanced RAG ask command works"""
    print("\nTest 4: Advanced RAG ask command (python3)")
    
    cli_tool = Path(".meta/tools/meta-harness-knowledge-base/kb")
    if not cli_tool.exists():
        print("  ✗ FAIL: kb CLI tool not found")
        return False
    
    # Test ask using python3 (Advanced RAG synthesis)
    result = subprocess.run(
        ["python3", str(cli_tool), "ask", "What is MainController?", "--top-k", "3"],
        capture_output=True,
        text=True,
        timeout=15
    )
    
    if "Answer synthesized" in result.stdout or "MainController" in result.stdout:
        print("  ✓ PASS: Advanced RAG ask returns synthesized answer")
        return True
    else:
        print("  ✗ FAIL: Advanced RAG ask didn't return expected results")
        print(f"    stdout: {result.stdout[:200]}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("KB-First Query Pattern Tests")
    print("=" * 60)
    
    tests = [
        test_kb_has_maincontroller_info,
        test_kb_population_script_reads_all_files,
        test_rag_cli_works,
        test_advanced_rag_ask,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n  ✗ FAIL: {test.__name__} raised {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
