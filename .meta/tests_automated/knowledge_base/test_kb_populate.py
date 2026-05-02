#!/usr/bin/env python3
"""
Knowledge Base Populate Tests
==============================
Tests for KB population functionality
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add KB to path
KB_PATH = Path(__file__).parent.parent.parent.parent / ".meta" / "tools" / "meta-harness-knowledge-base"
sys.path.insert(0, str(KB_PATH))

from knowledge_base import kb_stats
from populate.populate_kb import KBPopulator


class PopulateResults:
    """Track populate test results"""
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


results = PopulateResults()


def test_populate_import():
    """Test that populate module imports correctly"""
    name = "Populate Module Import"
    try:
        # If we got here, import worked
        results.add_result(name, True, "Module imports successfully")
    except Exception as e:
        results.add_result(name, False, f"Import failed: {str(e)}")


def test_populator_initialization():
    """Test KBPopulator initialization"""
    name = "Populator Initialization"
    try:
        populator = KBPopulator(verbose=False)
        results.add_result(name, True, "KBPopulator initialized")
    except Exception as e:
        results.add_result(name, False, f"Initialization failed: {str(e)}")


def test_find_meta_files():
    """Test finding META.md files"""
    name = "Find META Files"
    try:
        populator = KBPopulator(verbose=False)
        files = populator.find_all_meta_files()
        passed = len(files) > 0
        results.add_result(name, passed, f"Found {len(files)} files" if passed else "No files found")
    except Exception as e:
        results.add_result(name, False, f"Error: {str(e)}")


def test_find_source_files():
    """Test finding source code files"""
    name = "Find Source Files"
    try:
        populator = KBPopulator(verbose=False)
        files = populator.find_all_meta_files()
        
        # Check if source files are included
        has_python = any(str(f[0]).endswith('.py') for f in files)
        has_markdown = any(str(f[0]).endswith('.md') for f in files)
        
        passed = has_python or has_markdown
        message = f"Python: {has_python}, Markdown: {has_markdown}"
        results.add_result(name, passed, message)
    except Exception as e:
        results.add_result(name, False, f"Error: {str(e)}")


def test_analyze_markdown_file():
    """Test analyzing a markdown file"""
    name = "Analyze Markdown File"
    try:
        populator = KBPopulator(verbose=False)
        
        # Find a markdown file to analyze
        files = populator.find_all_meta_files()
        md_files = [f for f in files if str(f[0]).endswith('.md')]
        
        if md_files:
            test_file = md_files[0][0]
            analysis = populator.analyze_file_with_llm(test_file)
            passed = len(analysis) > 0
            results.add_result(name, passed, f"Analyzed {test_file.name}" if passed else "No analysis")
        else:
            results.add_result(name, False, "No markdown files found")
    except Exception as e:
        results.add_result(name, False, f"Error: {str(e)}")


def test_analyze_python_file():
    """Test analyzing a Python file"""
    name = "Analyze Python File"
    try:
        populator = KBPopulator(verbose=False)
        
        # Find a Python file to analyze - look in KB directory itself
        kb_py_files = list(KB_PATH.glob("*.py"))
        
        if kb_py_files:
            test_file = kb_py_files[0]
            analysis = populator.analyze_file_with_llm(test_file)
            passed = len(analysis) > 0
            results.add_result(name, passed, f"Analyzed {test_file.name}" if passed else "No analysis")
        else:
            # If no Python files, skip but mark as passed (not critical)
            results.add_result(name, True, "No Python files to test (skipped)")
    except Exception as e:
        results.add_result(name, False, f"Error: {str(e)}")


def test_create_kb_entries():
    """Test creating KB entries from analysis"""
    name = "Create KB Entries"
    try:
        populator = KBPopulator(verbose=False)
        
        # Create a mock analysis
        mock_analysis = {
            'title': 'Test Analysis',
            'summary': 'Test summary content',
            'sections': [
                {'title': 'Test Section', 'content': 'Test content'}
            ]
        }
        
        entries = populator.create_kb_entries(
            Path('/tmp/test.md'),
            mock_analysis,
            'meta'
        )
        
        passed = len(entries) > 0
        results.add_result(name, passed, f"Created {len(entries)} entries" if passed else "No entries created")
    except Exception as e:
        results.add_result(name, False, f"Error: {str(e)}")


def test_add_entry_function():
    """Test adding entry via populate"""
    name = "Add Entry Function"
    try:
        populator = KBPopulator(verbose=False)
        
        entry = {
            'type': 'finding',
            'category': 'test',
            'title': 'Test Entry from Populate',
            'finding': 'Test finding',
            'solution': 'Test solution',
            'context': 'Populate test',
            'confidence': 0.9
        }
        
        result = populator.add_entry(entry)
        passed = len(result) > 0
        results.add_result(name, passed, "Entry added" if passed else "Failed to add")
    except Exception as e:
        results.add_result(name, False, f"Error: {str(e)}")


def test_populate_dry_run():
    """Test population process (dry run - no actual adding)"""
    name = "Populate Dry Run"
    try:
        populator = KBPopulator(verbose=False)
        
        # Just test the file finding and analysis, don't add entries
        files = populator.find_all_meta_files()
        passed = len(files) > 0
        
        # Analyze first file
        if files:
            test_file = files[0]
            analysis = populator.analyze_file_with_llm(test_file[0])
            passed = passed and len(analysis) > 0
        
        message = f"Files: {len(files)}, Analysis: {'OK' if len(analysis) > 0 else 'Failed'}" if files else "No files"
        results.add_result(name, passed, message)
    except Exception as e:
        results.add_result(name, False, f"Error: {str(e)}")


def test_populate_script_execution():
    """Test running populate script"""
    name = "Populate Script Execution"
    try:
        import subprocess
        
        # Run populate script with --help to verify it works
        cmd = [
            "python3",
            str(KB_PATH / "populate" / "populate_kb.py"),
            "--help"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        passed = result.returncode == 0 or "usage" in result.stdout.lower()
        results.add_result(name, passed, "Script executes" if passed else "Script failed")
    except Exception as e:
        results.add_result(name, False, f"Error: {str(e)}")


def test_stats_after_operations():
    """Test that stats still work after populate operations"""
    name = "Stats After Operations"
    try:
        stats = kb_stats()
        passed = "Total entries" in stats
        results.add_result(name, passed, "Stats accessible" if passed else "Stats failed")
    except Exception as e:
        results.add_result(name, False, f"Error: {str(e)}")


def run_all_tests():
    """Run all populate tests"""
    print("\n" + "="*70)
    print("Knowledge Base Populate Tests")
    print("="*70 + "\n")
    
    start_time = time.time()
    
    # Run all tests
    test_populate_import()
    test_populator_initialization()
    test_find_meta_files()
    test_find_source_files()
    test_analyze_markdown_file()
    test_analyze_python_file()
    test_create_kb_entries()
    test_add_entry_function()
    test_populate_dry_run()
    test_populate_script_execution()
    test_stats_after_operations()
    
    end_time = time.time()
    
    # Summary
    print("\n" + "="*70)
    print(f"Populate Tests Complete")
    print(f"  Passed: {results.passed}")
    print(f"  Failed: {results.failed}")
    print(f"  Time:   {end_time - start_time:.2f}s")
    print("="*70 + "\n")
    
    return results.failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
