#!/usr/bin/env python3
"""
Meta Tools Facade - Dual Knowledge Base System

This module provides access to TWO separate knowledge bases:
1. Meta Harness KB - For Meta Project Harness patterns (.meta.data/kb-meta/knowledge-meta.db)
2. Agent-X KB - For Agent-X project knowledge (.meta.data/kb-meta/agent-x/agent-x.db)

Usage:
    from meta_tools import meta_kb, agentx_kb
    
    # Search Meta Harness KB
    meta_kb.kb_ask("Where should I write tests?")
    
    # Search Agent-X KB
    agentx_kb.kb_ask("How does the REPL work?")
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import sqlite3
import re
from datetime import datetime


class KnowledgeBase:
    """Wrapper for a knowledge base instance with its own DB path."""
    
    def __init__(self, db_path: Path):
        """Initialize KB with specific database path.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database if it doesn't exist."""
        if not self.db_path.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
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
            )""")
            
            cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts 
            USING fts5(id, type, category, title, confidence, context, finding, solution, example, created_at, updated_at)
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS corrections (
                id TEXT PRIMARY KEY,
                entry_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                new_finding TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                is_resolved INTEGER DEFAULT 0
            )""")
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS evolution_log (
                id INTEGER PRIMARY KEY,
                event_type TEXT NOT NULL,
                entry_id TEXT,
                old_value TEXT,
                new_value TEXT,
                reason TEXT,
                timestamp TEXT NOT NULL
            )""")
            
            conn.commit()
            conn.close()
    
    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout = 30000")
        return conn
    
    def kb_search(self, query: str, top_k: int = 5, category: Optional[str] = None) -> str:
        """Search knowledge base."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # Tokenize and escape FTS5 special characters
            tokens = re.findall(r'\b\w+\b', query.lower())
            escaped_query = ' OR '.join(tokens) if tokens else query
            
            category_filter = f"AND category = ?" if category else ""
            sql = f"""
            SELECT e.* FROM entries e
            JOIN entries_fts ON e.rowid = entries_fts.rowid
            WHERE entries_fts MATCH ?
            AND e.is_deprecated = 0
            {category_filter}
            ORDER BY bm25(entries_fts)
            LIMIT ?
            """
            
            params = [escaped_query, top_k] if not category else [escaped_query, category, top_k]
            cursor.execute(sql, params)
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return "No results found"
            
            formatted = []
            for row in results:
                formatted.append(
                    f"ID: {row['id']}\n"
                    f"Type: {row['type']} | Category: {row['category']} | Confidence: {row['confidence']:.2f}\n"
                    f"Title: {row['title']}\n"
                    f"Finding: {row['finding'] or 'N/A'}\n"
                    f"Solution: {row['solution'] or 'N/A'}\n"
                )
            return "\n\n".join(formatted)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def kb_ask(self, question: str, top_k: int = 3) -> str:
        """Ask a question with RAG."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # Tokenize question for FTS5
            tokens = re.findall(r'\b\w+\b', question.lower())
            escaped_query = ' OR '.join(tokens) if tokens else question
            
            sql = """
            SELECT e.* FROM entries e
            JOIN entries_fts ON e.rowid = entries_fts.rowid
            WHERE entries_fts MATCH ?
            AND e.is_deprecated = 0
            ORDER BY bm25(entries_fts)
            LIMIT ?
            """
            
            cursor.execute(sql, (escaped_query, top_k))
            results = cursor.fetchall()
            conn.close()
            
            prompt = "You are an AI agent working on the Agent-X project.\n"
            prompt += "Use the following retrieved knowledge from the project's knowledge base to answer the question.\n\n"
            
            if results:
                prompt += "### Retrieved Knowledge:\n\n"
                for i, row in enumerate(results, 1):
                    prompt += f"[{i}] **{row['title']}** (`{row['id']}`)\n"
                    prompt += f" Type: {row['type']} | Category: {row['category']} | Confidence: {row['confidence']:.2f}\n"
                    if row['finding']:
                        prompt += f" Finding: {row['finding']}\n"
                    if row['solution']:
                        prompt += f" Solution: {row['solution']}\n"
                    prompt += "\n"
            else:
                prompt += "No relevant knowledge found in the project knowledge base. Answer based on general knowledge.\n\n"
            
            prompt += f"### Question:\n{question}\n\n### Your Answer:\n"
            return prompt
        except Exception as e:
            return f"Error: {str(e)}"
    
    def kb_add_entry(self, entry_type: str, category: str, title: str, finding: str,
                     solution: str, context: str = "", confidence: float = 0.5, example: str = "") -> str:
        """Add new entry."""
        try:
            import hashlib
            import random
            
            conn = self._get_conn()
            cursor = conn.cursor()
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
            random_val = random.randint(0, 9999)
            hash_input = f"{entry_type}{category}{timestamp}{random_val}"
            hash_val = hashlib.md5(hash_input.encode()).hexdigest()[:4].upper()
            prefix_map = {'pattern': 'PAT', 'finding': 'FIND', 'correction': 'COR', 'decision': 'DEC'}
            entry_id = f"{prefix_map.get(entry_type, 'KB')}-{hash_val}"
            
            now = datetime.now().isoformat()
            
            cursor.execute("""
            INSERT INTO entries (id, type, category, title, confidence, context,
            finding, solution, example, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (entry_id, entry_type, category, title, confidence, context,
                  finding, solution, example, now, now))
            
            conn.commit()
            conn.close()
            
            return f"Added {entry_type.upper()} entry: {entry_id} - {title}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def kb_correct(self, entry_id: str, reason: str, new_finding: str) -> str:
        """Add correction."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, confidence FROM entries WHERE id = ?", (entry_id,))
            entry = cursor.fetchone()
            
            if not entry:
                conn.close()
                return f"Error: Entry {entry_id} not found"
            
            import hashlib
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            hash_input = f"correction{entry_id}{timestamp}"
            hash_val = hashlib.md5(hash_input.encode()).hexdigest()[:4].upper()
            correction_id = f"COR-{hash_val}"
            
            now = datetime.now().isoformat()
            
            cursor.execute("""
            INSERT INTO corrections (id, entry_id, reason, new_finding, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """, (correction_id, entry_id, reason, new_finding, now))
            
            new_confidence = max(0.0, entry['confidence'] - 0.20)
            
            cursor.execute("""
            UPDATE entries SET confidence = ?, updated_at = ? WHERE id = ?
            """, (new_confidence, now, entry_id))
            
            conn.commit()
            conn.close()
            
            return f"Added correction to {entry_id}. Confidence: {entry['confidence']:.2f} → {new_confidence:.2f}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def kb_evolve(self) -> str:
        """Run evolution cycle."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            cursor.execute("""
            UPDATE entries SET confidence = MAX(0.0, confidence - 0.05), updated_at = ?
            WHERE last_used_at IS NULL AND created_at < datetime('now', '-30 days') AND is_deprecated = 0
            """, (datetime.now().isoformat(),))
            decayed = cursor.rowcount
            
            cursor.execute("""
            UPDATE entries SET is_deprecated = 1 WHERE confidence < 0.3 AND is_deprecated = 0
            """)
            archived = cursor.rowcount
            
            cursor.execute("SELECT COUNT(*) FROM corrections WHERE is_resolved = 0")
            pending = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            
            return f"Evolution complete: {decayed} decayed, {archived} archived, {pending} pending corrections"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def kb_stats(self) -> str:
        """Get statistics."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT type, COUNT(*) as count, AVG(confidence) as avg_conf
            FROM entries WHERE is_deprecated = 0 GROUP BY type
            """)
            by_type = {row['type']: {"count": row['count'], "avg_confidence": row['avg_conf'] or 0} for row in cursor.fetchall()}
            
            cursor.execute("""
            SELECT category, COUNT(*) as count FROM entries WHERE is_deprecated = 0 GROUP BY category
            """)
            by_category = {row['category']: row['count'] for row in cursor.fetchall()}
            
            cursor.execute("""
            SELECT
            SUM(CASE WHEN confidence >= 0.9 THEN 1 ELSE 0 END) as high,
            SUM(CASE WHEN confidence BETWEEN 0.6 AND 0.9 THEN 1 ELSE 0 END) as medium,
            SUM(CASE WHEN confidence < 0.6 THEN 1 ELSE 0 END) as low
            FROM entries WHERE is_deprecated = 0
            """)
            row = cursor.fetchone()
            confidence_dist = {
                "high": row[0] or 0,
                "medium": row[1] or 0,
                "low": row[2] or 0
            }
            
            cursor.execute("SELECT COUNT(*) FROM corrections WHERE is_resolved = 0")
            pending_corrections = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM entries WHERE is_deprecated = 0")
            total = cursor.fetchone()[0]
            
            conn.close()
            
            lines = [f"Total entries: {total}"]
            lines.append("\nBy type:")
            for type_name, data in by_type.items():
                lines.append(f" {type_name}: {data['count']} (avg confidence: {data['avg_confidence']:.2f})")
            lines.append("\nBy category:")
            for cat, count in by_category.items():
                lines.append(f" {cat}: {count}")
            lines.append(f"\nConfidence distribution:")
            lines.append(f" High (>=0.9): {confidence_dist['high']}")
            lines.append(f" Medium (0.6-0.9): {confidence_dist['medium']}")
            lines.append(f" Low (<0.6): {confidence_dist['low']}")
            lines.append(f"\nPending corrections: {pending_corrections}")
            
            return "\n".join(lines)
        except Exception as e:
            return f"Error: {str(e)}"


# Create two KB instances
META_KB_PATH = Path(__file__).parent.parent / ".meta.data" / "kb-meta" / "knowledge-meta.db"
AGENTX_KB_PATH = Path(__file__).parent.parent / ".meta.data" / "kb-meta" / "agent-x" / "agent-x.db"

# Initialize KB instances
meta_kb = KnowledgeBase(META_KB_PATH)
agentx_kb = KnowledgeBase(AGENTX_KB_PATH)

# Export default to meta_kb for backward compatibility
kb_ask = meta_kb.kb_ask
kb_search = meta_kb.kb_search
kb_add_entry = meta_kb.kb_add_entry
kb_correct = meta_kb.kb_correct
kb_evolve = meta_kb.kb_evolve
kb_stats = meta_kb.kb_stats

__all__ = [
    "meta_kb",
    "agentx_kb",
    "kb_ask",
    "kb_search",
    "kb_add_entry",
    "kb_correct",
    "kb_evolve",
    "kb_stats",
]


# Test if run directly
if __name__ == "__main__":
    print("=== Meta Tools Test ===\n")
    
    print("--- Meta Harness KB ---")
    print("Stats:")
    print(meta_kb.kb_stats())
    
    print("\nSearch 'TDD':")
    print(meta_kb.kb_search("TDD", top_k=2))
    
    print("\nAsk 'Where should I write tests?':")
    print(meta_kb.kb_ask("Where should I write tests?")[:500] + "...")
    
    print("\n--- Agent-X KB ---")
    print("Stats:")
    print(agentx_kb.kb_stats())
    
    print("\nSearch 'REPL':")
    print(agentx_kb.kb_search("REPL", top_k=2))
