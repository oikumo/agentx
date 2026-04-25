#!/usr/bin/env python3
"""Initialize the knowledge base database."""

import sqlite3
from pathlib import Path

def init_db(DB_PATH: Path):
    """Initialize the knowledge base database schema.
    
    Args:
        DB_PATH: Path to the database file
    """
    # Create parent directory if it doesn't exist
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(DB_PATH))
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
    
    # Create FTS virtual table for full-text search
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
    
    # Create triggers to keep FTS in sync
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS entries_ai AFTER INSERT ON entries BEGIN
        INSERT INTO entries_fts(rowid, id, type, category, title, confidence, context, finding, solution, example, created_at, updated_at)
        VALUES (NEW.rowid, NEW.id, NEW.type, NEW.category, NEW.title, NEW.confidence, NEW.context, NEW.finding, NEW.solution, NEW.example, NEW.created_at, NEW.updated_at);
    END
    """)
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS entries_ad AFTER DELETE ON entries BEGIN
        DELETE FROM entries_fts WHERE rowid=OLD.rowid;
    END
    """)
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS entries_au AFTER UPDATE ON entries BEGIN
        DELETE FROM entries_fts WHERE rowid=OLD.rowid;
        INSERT INTO entries_fts(rowid, id, type, category, title, confidence, context, finding, solution, example, created_at, updated_at)
        VALUES (NEW.rowid, NEW.id, NEW.type, NEW.category, NEW.title, NEW.confidence, NEW.context, NEW.finding, NEW.solution, NEW.example, NEW.created_at, NEW.updated_at);
    END
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    # Default path: project root/.meta.data/kb-meta/
    KB_PATH = Path(__file__).parent.parent.parent.parent / ".meta.data" / "kb-meta"
    DB_PATH = KB_PATH / "knowledge-meta.db"
    init_db(DB_PATH)
