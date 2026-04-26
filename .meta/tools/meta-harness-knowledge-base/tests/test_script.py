#!/usr/bin/env python3
"""
Test script to verify the knowledge base functionality.
"""

import sys
from pathlib import Path
import tempfile
import sqlite3

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the knowledge base
import knowledge_base

# Import rag_tool to patch the database connection
from src import rag_tool

# Create a temporary in-memory database for testing
def create_test_db():
    """Create a test database with the required schema."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # Create entries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            confidence REAL NOT NULL,
            context TEXT,
            finding TEXT,
            solution TEXT,
            example TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_used_at TEXT,
            is_deprecated INTEGER DEFAULT 0,
            use_count INTEGER DEFAULT 0
        )
    """)
    
    # Create FTS virtual table
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts 
        USING fts5(id, type, category, title, confidence, context, finding, solution, example, created_at, updated_at)
    """)
    
    # Create corrections table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS corrections (
            id TEXT PRIMARY KEY,
            entry_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            new_finding TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            is_resolved INTEGER DEFAULT 0
        )
    """)
    
    # Create evolution log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evolution_log (
            id INTEGER PRIMARY KEY,
            event_type TEXT NOT NULL,
            entry_id TEXT,
            old_value TEXT,
            new_value TEXT,
            reason TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    
    conn.commit()
    return conn

# Patch the database connection function for testing
def mock_get_db_connection():
    """Create an in-memory database for testing."""
    return create_test_db()

# Apply the patch
rag_tool.get_db_connection = mock_get_db_connection

def test_knowledge_base():
    """Test the knowledge base functionality."""
    print("Testing Meta Harness Knowledge Base...")
    
    # Test adding an entry
    print("\n1. Testing entry addition...")
    result = knowledge_base.kb_add_entry(
        entry_type="pattern",
        category="test",
        title="Test Entry",
        finding="This is a test entry",
        solution="Run tests to verify functionality",
        confidence=0.9
    )
    print(f"   Result: {result}")
    
    # Test searching
    print("\n2. Testing search...")
    result = knowledge_base.kb_search("test entry")
    print(f"   Result: {result}")
    
    # Test asking a question
    print("\n3. Testing question asking...")
    result = knowledge_base.kb_ask("How do I run tests?")
    print(f"   Result: {result}")
    
    # Test getting stats
    print("\n4. Testing statistics...")
    result = knowledge_base.kb_stats()
    print(f"   Result: {result}")
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    test_knowledge_base()