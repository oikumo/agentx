#!/usr/bin/env python3
"""
TDD Test: Opencode KB-First Behavior

This test validates that opencode queries the KB FIRST when asked
"What is MainController?"

Expected behavior:
1. User asks: "What is MainController?"
2. Opencode MUST run: python3 .meta/tools/meta-harness-knowledge-base/kb ask "What is MainController?" --top-k 3
3. Opencode MUST answer from KB results
4. Opencode MUST cite KB entries

FAIL if opencode searches code (grep/glob) before querying KB.
"""

import subprocess
import sys
import time
from pathlib import Path

def test_opencode_uses_kb_first():
    """
    Test that opencode queries KB before searching code.
    
    This is a BEHAVIORAL test - it checks the actual output from opencode
    to see if it queried KB first.
    """
    print("=" * 70)
    print("TDD Test: Opencode KB-First Behavior")
    print("=" * 70)
    print()
    
    # The question to ask
    question = "What is MainController?"
    
    print(f"Question: {question}")
    print()
    print("Expected behavior:")
    print("  1. Opencode queries KB using Advanced RAG")
    print("  2. Command: python3 .meta/tools/meta-harness-knowledge-base/kb ask")
    print("  3. Answer cites KB entries")
    print()
    print("FAIL behavior:")
    print("  - Opencode runs grep/glob BEFORE kb ask")
    print("  - No KB citation in response")
    print()
    
    # Run opencode and capture output
    print("Running opencode run...")
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ["opencode", "run", question],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        elapsed = time.time() - start_time
        output = result.stdout + result.stderr
        
        print(f"\nOpencode output ({elapsed:.1f}s):")
        print("-" * 70)
        print(output[:2000])  # First 2000 chars
        print("-" * 70)
        
        # Check if KB was queried first
        kb_query_keywords = [
            "kb ask",
            "knowledge base",
            "kb search",
            "meta-harness-knowledge-base",
        ]
        
        code_search_keywords = [
            "grep",
            "glob",
            "searching",
            "looking for",
        ]
        
        # Analyze output
        kb_found = any(kw in output.lower() for kw in kb_query_keywords)
        code_search = any(kw in output.lower() for kw in code_search_keywords)
        
        print("\nAnalysis:")
        if kb_found:
            print("  ✓ KB query detected")
        else:
            print("  ✗ NO KB query detected")
            
        if code_search:
            print("  ⚠ Code search detected (grep/glob)")
        else:
            print("  ✓ No code search detected")
        
        # Determine pass/fail
        if kb_found and not code_search:
            print("\n✓ PASS: Opencode queried KB first")
            return True
        elif code_search and not kb_found:
            print("\n✗ FAIL: Opencode searched code WITHOUT querying KB first")
            return False
        elif kb_found and code_search:
            # Check which came first
            kb_pos = min(output.lower().find(kw) for kw in kb_query_keywords if kw in output.lower())
            search_pos = min(output.lower().find(kw) for kw in code_search_keywords if kw in output.lower())
            
            if kb_pos < search_pos:
                print("\n✓ PASS: KB query came before code search")
                return True
            else:
                print("\n✗ FAIL: Code search came before KB query")
                return False
        else:
            print("\n? UNKNOWN: Could not determine behavior")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n✗ FAIL: Opencode timed out (took > 60s)")
        return False
    except Exception as e:
        print(f"\n✗ FAIL: Exception occurred: {e}")
        return False

def test_kb_tool_works():
    """Verify the KB tool itself works (prerequisite)"""
    print("\n" + "=" * 70)
    print("Prerequisite Test: KB Tool Functionality")
    print("=" * 70)
    
    kb_tool = Path(".meta/tools/meta-harness-knowledge-base/kb")
    if not kb_tool.exists():
        print("  ✗ FAIL: KB tool not found")
        return False
    
    result = subprocess.run(
        ["python3", str(kb_tool), "ask", "What is MainController?", "--top-k", "1"],
        capture_output=True,
        text=True,
        timeout=15
    )
    
    if "MainController" in result.stdout or "Answer synthesized" in result.stdout:
        print("  ✓ PASS: KB tool returns MainController info")
        print(f"  Output: {result.stdout[:200]}...")
        return True
    else:
        print("  ✗ FAIL: KB tool didn't return expected results")
        print(f"  Output: {result.stdout[:200]}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("TDD: Opencode KB-First Implementation")
    print("=" * 70)
    print()
    
    # Test 1: Prerequisite - KB tool must work
    kb_works = test_kb_tool_works()
    
    if not kb_works:
        print("\n✗ STOP: KB tool is not working. Fix prerequisite first.")
        return False
    
    # Test 2: Main test - Opencode behavior
    print("\n" + "=" * 70)
    print("MAIN TEST: Opencode KB-First Behavior")
    print("=" * 70)
    print()
    
    opencode_ok = test_opencode_uses_kb_first()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"KB Tool:        {'✓ PASS' if kb_works else '✗ FAIL'}")
    print(f"Opencode KB-First: {'✓ PASS' if opencode_ok else '✗ FAIL'}")
    print("=" * 70)
    
    if opencode_ok:
        print("\n✓ All tests passed!")
        return True
    else:
        print("\n✗ Opencode is NOT querying KB first.")
        print("\nRequired fix:")
        print("  - Opencode needs to be configured to use KB-First skill")
        print("  - Or AGENTS.md rules need to be enforced")
        print("  - Or a wrapper script is needed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
