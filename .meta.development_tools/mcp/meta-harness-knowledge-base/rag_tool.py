#!/usr/bin/env python3
"""
MCP Tool: Knowledge Base RAG for opencode

This tool allows opencode to query the Meta Project Harness Knowledge Base
using RAG (Retrieval-Augmented Generation) to get context-aware answers.

The tool:
1. Receives a query from opencode
2. Retrieves relevant knowledge from KB
3. Augments the query with context
4. Returns enriched prompt for LLM

Usage (via MCP):
  - rag_search(query, top_k=5, category=None)
  - rag_ask(question, top_k=3)
  - rag_add_entry(type, category, title, finding, solution, context, confidence)
  - rag_correct(entry_id, reason, new_finding)
  - rag_evolve()
  - rag_stats()
"""

import sys
import json
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

# Path to knowledge base (go up from .meta.development_tools/mcp/meta-harness-knowledge-base to project root)
KB_PATH = Path(__file__).parent.parent.parent.parent / ".meta.knowledge_base"
DB_PATH = KB_PATH / "knowledge.db"

# Add KB to path for imports
sys.path.insert(0, str(KB_PATH))


def get_db_connection():
    """Get SQLite connection with proper isolation."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Knowledge base not found at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")  # Wait 30s for locks
    return conn


def simple_tokenize(text: str) -> List[str]:
    """Simple tokenization."""
    return re.findall(r'\b\w+\b', text.lower())


def keyword_score(text: str, query: str) -> float:
    """Keyword matching score."""
    if not text:
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
    
    # Query expansion: also search for individual words
    tokens = simple_tokenize(query)
    if len(tokens) > 1:
        # Search for individual tokens OR'd together
        fts_query = " OR ".join(tokens)
    else:
        fts_query = query
    
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
        
        # Combined: BM25 + keyword + confidence boost
        bm25_normalized = 1 / (1 - row['bm25_score'] + 0.1) if row['bm25_score'] else 0
        combined_score = 0.3 * bm25_normalized + 0.4 * kw_score + 0.3 * confidence
        scored_results.append((combined_score, dict(row)))
    
    scored_results.sort(key=lambda x: x[0], reverse=True)
    return [result for score, result in scored_results[:top_k]]


def rag_search(query: str, top_k: int = 5, category: Optional[str] = None) -> Dict[str, Any]:
    """
    Search knowledge base and return relevant entries.
    
    Args:
        query: Search query
        top_k: Number of results (default: 5)
        category: Optional category filter
    
    Returns:
        Dictionary with results and metadata
    """
    try:
        conn = get_db_connection()
        results = hybrid_search(conn, query, category, top_k)
        conn.close()
        
        # Format for LLM consumption
        formatted_results = []
        for entry in results:
            formatted_results.append({
                "id": entry["id"],
                "type": entry["type"],
                "category": entry["category"],
                "title": entry["title"],
                "confidence": entry["confidence"],
                "context": entry.get("context", ""),
                "finding": entry.get("finding", ""),
                "solution": entry.get("solution", ""),
                "example": entry.get("example", ""),
            })
        
        return {
            "success": True,
            "query": query,
            "count": len(formatted_results),
            "results": formatted_results,
            "message": f"Found {len(formatted_results)} relevant entries" if formatted_results else "No results found"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Search failed: {str(e)}"
        }


def rag_ask(question: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Ask a question and get RAG-augmented response.
    
    This retrieves relevant knowledge and formats it as context
    for the LLM to generate an answer.
    
    Args:
        question: User question
        top_k: Number of context entries (default: 3)
    
    Returns:
        Dictionary with augmented prompt and retrieved context
    """
    try:
        conn = get_db_connection()
        results = hybrid_search(conn, question, None, top_k)
        conn.close()
        
        # Build augmented prompt
        prompt = """You are an AI agent working on the Agent-X project.
Use the following retrieved knowledge from the project's knowledge base to answer the question.

"""
        if results:
            prompt += "### Retrieved Knowledge:\n\n"
            for i, entry in enumerate(results, 1):
                prompt += f"[{i}] **{entry['title']}** (`{entry['id']}`)\n"
                prompt += f"    Type: {entry['type']} | Category: {entry['category']} | Confidence: {entry['confidence']:.2f}\n"
                if entry.get('finding'):
                    prompt += f"    Finding: {entry['finding']}\n"
                if entry.get('solution'):
                    prompt += f"    Solution: {entry['solution']}\n"
                if entry.get('example'):
                    prompt += f"    Example: {entry['example']}\n"
                prompt += "\n"
        else:
            prompt += "No relevant knowledge found in the project knowledge base. Answer based on general knowledge.\n\n"
        
        prompt += f"### Question:\n{question}\n\n### Your Answer:\n"
        
        # Format results for response
        formatted_results = []
        for entry in results:
            formatted_results.append({
                "id": entry["id"],
                "title": entry["title"],
                "type": entry["type"],
                "confidence": entry["confidence"],
                "finding": entry.get("finding", ""),
                "solution": entry.get("solution", ""),
            })
        
        return {
            "success": True,
            "question": question,
            "augmented_prompt": prompt,
            "context_count": len(formatted_results),
            "retrieved_context": formatted_results,
            "message": f"Retrieved {len(formatted_results)} relevant entries. Use the augmented_prompt to answer."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"RAG ask failed: {str(e)}"
        }


def rag_add_entry(entry_type: str, category: str, title: str, finding: str,
    solution: str, context: str = "", confidence: float = 0.5, example: str = "") -> Dict[str, Any]:
    """
    Add new knowledge entry to the knowledge base.

    Args:
        entry_type: Type of entry (pattern, finding, correction, decision)
        category: Category (workflow, code, test, docs, tool, architecture)
        title: Concise title
        finding: What was discovered
        solution: How to solve it
        context: When/where this applies
        confidence: Confidence score (0.0-1.0)
        example: Optional example

    Returns:
        Dictionary with result and entry ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Generate unique ID with timestamp and random component
        import hashlib
        import random
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

        return {
            "success": True,
            "entry_id": entry_id,
            "message": f"Added {entry_type.upper()} entry: {entry_id} - {title}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to add entry: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to add entry: {str(e)}"
        }


def rag_correct(entry_id: str, reason: str, new_finding: str) -> Dict[str, Any]:
    """
    Add correction to existing entry.
    
    Args:
        entry_id: ID of entry to correct
        reason: Why correction is needed
        new_finding: Updated information
    
    Returns:
        Dictionary with result
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if entry exists
        cursor.execute("SELECT id, confidence FROM entries WHERE id = ?", (entry_id,))
        entry = cursor.fetchone()
        
        if not entry:
            conn.close()
            return {
                "success": False,
                "error": f"Entry {entry_id} not found",
                "message": f"Entry {entry_id} not found"
            }
        
        import hashlib
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        hash_input = f"correction{entry_id}{timestamp}"
        hash_val = hashlib.md5(hash_input.encode()).hexdigest()[:4].upper()
        correction_id = f"COR-{hash_val}"
        
        now = datetime.now().isoformat()
        
        # Add correction
        cursor.execute("""
            INSERT INTO corrections (id, entry_id, reason, new_finding, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (correction_id, entry_id, reason, new_finding, now))
        
        # Adjust confidence
        old_confidence = entry['confidence']
        new_confidence = max(0.0, old_confidence - 0.20)
        
        cursor.execute("""
            UPDATE entries 
            SET confidence = ?, updated_at = ?
            WHERE id = ?
        """, (new_confidence, now, entry_id))
        
        # Log evolution
        cursor.execute("""
            INSERT INTO evolution_log (event_type, entry_id, old_value, new_value, reason)
            VALUES (?, ?, ?, ?, ?)
        """, ('correction', entry_id, str(old_confidence), str(new_confidence), reason))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "correction_id": correction_id,
            "old_confidence": old_confidence,
            "new_confidence": new_confidence,
            "message": f"Added correction to {entry_id}. Confidence: {old_confidence:.2f} → {new_confidence:.2f}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Correction failed: {str(e)}"
        }


def rag_evolve() -> Dict[str, Any]:
    """
    Run evolution cycle: decay unused entries, archive low confidence.
    
    Returns:
        Dictionary with evolution results
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Decay unused entries
        cursor.execute("""
            UPDATE entries 
            SET confidence = MAX(0.0, confidence - 0.05),
                updated_at = ?
            WHERE last_used_at IS NULL 
              AND created_at < datetime('now', '-30 days')
              AND is_deprecated = 0
        """, (datetime.now().isoformat(),))
        decayed = cursor.rowcount
        
        # Archive low confidence
        cursor.execute("""
            UPDATE entries 
            SET is_deprecated = 1
            WHERE confidence < 0.3 AND is_deprecated = 0
        """)
        archived = cursor.rowcount
        
        # Count pending corrections
        cursor.execute("SELECT COUNT(*) FROM corrections WHERE is_resolved = 0")
        pending = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "decayed": decayed,
            "archived": archived,
            "pending_corrections": pending,
            "message": f"Evolution complete: {decayed} decayed, {archived} archived, {pending} pending corrections"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Evolution failed: {str(e)}"
        }


def rag_stats() -> Dict[str, Any]:
    """
    Get knowledge base statistics.
    
    Returns:
        Dictionary with statistics
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # By type
        cursor.execute("""
            SELECT type, COUNT(*) as count, AVG(confidence) as avg_conf
            FROM entries WHERE is_deprecated = 0
            GROUP BY type
        """)
        by_type = {row['type']: {"count": row['count'], "avg_confidence": row['avg_conf']} for row in cursor.fetchall()}
        
        # By category
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM entries WHERE is_deprecated = 0
            GROUP BY category
        """)
        by_category = {row['category']: row['count'] for row in cursor.fetchall()}
        
        # Confidence distribution
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
        
        # Pending corrections
        cursor.execute("SELECT COUNT(*) FROM corrections WHERE is_resolved = 0")
        pending_corrections = cursor.fetchone()[0]
        
        # Total entries
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
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Stats failed: {str(e)}"
        }


# Export functions for MCP tool
__all__ = [
    "rag_search",
    "rag_ask",
    "rag_add_entry",
    "rag_correct",
    "rag_evolve",
    "rag_stats",
]


# Test if run directly
if __name__ == "__main__":
    print("Testing RAG tool...")
    
    # Test search
    print("\n1. Search test:")
    result = rag_search("TDD", top_k=3)
    print(json.dumps(result, indent=2))
    
    # Test ask
    print("\n2. Ask test:")
    result = rag_ask("Where should I write tests?")
    print(json.dumps(result, indent=2))
    
    # Test stats
    print("\n3. Stats test:")
    result = rag_stats()
    print(json.dumps(result, indent=2))
