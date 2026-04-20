#!/usr/bin/env python3
"""
Core knowledge base operations - stdlib only, no external dependencies.
"""

import sqlite3
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Paths
KB_PATH = Path(__file__).parent.parent
DB_PATH = KB_PATH / "knowledge.db"
SCHEMA_PATH = KB_PATH / "schemas" / "v1_schema.sql"


def get_db_connection():
    """Get SQLite connection with FTS5 support."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize database with schema if not exists."""
    if not DB_PATH.exists():
        conn = get_db_connection()
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
    return get_db_connection()


def simple_tokenize(text: str) -> List[str]:
    """Simple tokenization for keyword matching."""
    return re.findall(r'\b\w+\b', text.lower()) if text else []


def keyword_score(text: str, query: str) -> float:
    """Calculate keyword matching score."""
    if not text or not query:
        return 0.0
    text_tokens = set(simple_tokenize(text))
    query_tokens = set(simple_tokenize(query))
    if not query_tokens:
        return 0.0
    matches = len(text_tokens & query_tokens)
    return matches / len(query_tokens)


def hybrid_search(conn, query: str, category: Optional[str] = None, top_k: int = 5) -> List[Dict]:
    """Hybrid search: FTS5 + keyword matching with query expansion."""
    cursor = conn.cursor()
    
    # Query expansion for better FTS5 matching
    tokens = simple_tokenize(query)
    fts_query = " OR ".join(tokens) if len(tokens) > 1 else query
    category_filter = f"AND category = '{category}'" if category else ""
    
    sql = f"""
        SELECT e.*, bm25(entries_fts) as bm25_score
        FROM entries e
        JOIN entries_fts ON e.rowid = entries_fts.rowid
        WHERE entries_fts MATCH ?
        {category_filter}
        AND e.is_deprecated = 0
        ORDER BY bm25_score
        LIMIT ?
    """
    
    cursor.execute(sql, (fts_query, top_k * 2))
    fts_results = cursor.fetchall()
    
    # Re-rank by keyword + confidence
    scored_results = []
    for row in fts_results:
        text = f"{row['title']} {row['context']} {row['finding']} {row['solution']}"
        kw_score = keyword_score(text, query)
        confidence = row['confidence']
        bm25_normalized = 1 / (1 - row['bm25_score'] + 0.1) if row['bm25_score'] else 0
        combined_score = 0.3 * bm25_normalized + 0.4 * kw_score + 0.3 * confidence
        scored_results.append((combined_score, dict(row)))
    
    scored_results.sort(key=lambda x: x[0], reverse=True)
    return [result for score, result in scored_results[:top_k]]


def generate_id(entry_type: str, category: str) -> str:
    """Generate unique ID for entry."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_input = f"{entry_type}{category}{timestamp}"
    hash_val = hashlib.md5(hash_input.encode()).hexdigest()[:4].upper()
    prefix_map = {'pattern': 'PAT', 'finding': 'FIND', 'correction': 'COR', 'decision': 'DEC'}
    return f"{prefix_map.get(entry_type, 'KB')}-{hash_val}"


def add_entry(entry_type: str, category: str, title: str, finding: str, 
              solution: str, context: str = "", example: str = "", 
              confidence: float = 0.5) -> Dict[str, Any]:
    """Add new knowledge entry."""
    conn = init_db()
    cursor = conn.cursor()
    entry_id = generate_id(entry_type, category)
    now = datetime.now().isoformat()
    
    try:
        cursor.execute("""
            INSERT INTO entries (id, type, category, title, confidence, context, 
                                finding, solution, example, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (entry_id, entry_type, category, title, confidence, context,
              finding, solution, example, now, now))
        
        conn.commit()
        return {"success": True, "entry_id": entry_id, "message": f"Added {entry_type.upper()}: {entry_id}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def correct_entry(entry_id: str, reason: str, new_finding: str) -> Dict[str, Any]:
    """Add correction to existing entry."""
    conn = init_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, confidence FROM entries WHERE id = ?", (entry_id,))
    entry = cursor.fetchone()
    
    if not entry:
        conn.close()
        return {"success": False, "error": f"Entry {entry_id} not found"}
    
    correction_id = generate_id("correction", "auto")
    now = datetime.now().isoformat()
    old_confidence = entry['confidence']
    new_confidence = max(0.0, old_confidence - 0.20)
    
    try:
        cursor.execute("""
            INSERT INTO corrections (id, entry_id, reason, new_finding, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (correction_id, entry_id, reason, new_finding, now))
        
        cursor.execute("""
            UPDATE entries SET confidence = ?, updated_at = ? WHERE id = ?
        """, (new_confidence, now, entry_id))
        
        cursor.execute("""
            INSERT INTO evolution_log (event_type, entry_id, old_value, new_value, reason)
            VALUES (?, ?, ?, ?, ?)
        """, ('correction', entry_id, str(old_confidence), str(new_confidence), reason))
        
        conn.commit()
        return {
            "success": True,
            "correction_id": correction_id,
            "old_confidence": old_confidence,
            "new_confidence": new_confidence,
            "message": f"Corrected {entry_id}. Confidence: {old_confidence:.2f} → {new_confidence:.2f}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def run_evolution() -> Dict[str, Any]:
    """Run evolution cycle: decay and archive."""
    conn = init_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE entries SET confidence = MAX(0.0, confidence - 0.05), updated_at = ?
        WHERE last_used_at IS NULL AND created_at < datetime('now', '-30 days') AND is_deprecated = 0
    """, (datetime.now().isoformat(),))
    decayed = cursor.rowcount
    
    cursor.execute("UPDATE entries SET is_deprecated = 1 WHERE confidence < 0.3 AND is_deprecated = 0")
    archived = cursor.rowcount
    
    cursor.execute("SELECT COUNT(*) FROM corrections WHERE is_resolved = 0")
    pending = cursor.fetchone()[0]
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "decayed": decayed,
        "archived": archived,
        "pending_corrections": pending,
        "message": f"Evolution: {decayed} decayed, {archived} archived, {pending} pending"
    }


def get_stats() -> Dict[str, Any]:
    """Get knowledge base statistics."""
    conn = init_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT type, COUNT(*) as count, AVG(confidence) as avg_conf
        FROM entries WHERE is_deprecated = 0 GROUP BY type
    """)
    by_type = {row['type']: {"count": row['count'], "avg_confidence": row['avg_conf']} for row in cursor.fetchall()}
    
    cursor.execute("""
        SELECT category, COUNT(*) as count FROM entries WHERE is_deprecated = 0 GROUP BY category
    """)
    by_category = {row['category']: row['count'] for row in cursor.fetchall()}
    
    cursor.execute("""
        SELECT SUM(CASE WHEN confidence >= 0.9 THEN 1 ELSE 0 END),
               SUM(CASE WHEN confidence BETWEEN 0.6 AND 0.9 THEN 1 ELSE 0 END),
               SUM(CASE WHEN confidence < 0.6 THEN 1 ELSE 0 END)
        FROM entries WHERE is_deprecated = 0
    """)
    row = cursor.fetchone()
    confidence_dist = {"high": row[0] or 0, "medium": row[1] or 0, "low": row[2] or 0}
    
    cursor.execute("SELECT COUNT(*) FROM corrections WHERE is_resolved = 0")
    pending_corrections = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM entries WHERE is_deprecated = 0")
    total = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "success": True,
        "total_entries": total,
        "by_type": by_type,
        "by_category": by_category,
        "confidence_distribution": confidence_dist,
        "pending_corrections": pending_corrections,
        "message": f"KB Stats: {total} entries, {pending_corrections} pending corrections"
    }


__all__ = [
    'get_db_connection', 'init_db', 'simple_tokenize', 'keyword_score',
    'hybrid_search', 'generate_id', 'add_entry', 'correct_entry', 
    'run_evolution', 'get_stats'
]
