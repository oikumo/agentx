#!/usr/bin/env python3
"""
MCP Tool: Knowledge Base RAG for opencode using ChromaDB

This tool allows opencode to query the Meta Project Harness Knowledge Base
using RAG (Retrieval-Augmented Generation) with ChromaDB as the vector store.
"""

import sys
import hashlib
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# ChromaDB imports
import chromadb
from chromadb.config import Settings

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def simple_tokenize(text: str) -> List[str]:
    """Simple tokenization."""
    return re.findall(r'\b\w+\b', text.lower()) if text else []


def escape_fts5_query(text: str) -> str:
    """Escape special characters for FTS5 query."""
    if not text:
        return ""
    special_chars = ['"', '*', '(', ')', ':', '-', '+', '~', '&', '|', '!', '{', '}', '[', ']', '^', '?', '\\']
    escaped = text
    for char in special_chars:
        escaped = escaped.replace(char, ' ')
    escaped = ' '.join(escaped.split())
    return escaped.strip()


def keyword_score(text: str, query: str) -> float:
    """Calculate keyword matching score with TF-IDF-like weighting."""
    if not text or not query:
        return 0.0
    
    text_tokens = simple_tokenize(text)
    query_tokens = simple_tokenize(query)
    
    if not query_tokens or not text_tokens:
        return 0.0
    
    text_set = set(text_tokens)
    query_set = set(query_tokens)
    
    matches = len(text_set & query_set)
    exact_match_bonus = 0.2 if query.lower() in text.lower() else 0.0
    coverage = matches / len(query_set) if query_set else 0.0
    specificity = matches / len(text_set) if text_set else 0.0
    
    return min(1.0, 0.5 * coverage + 0.3 * specificity + 0.2 * exact_match_bonus)


def semantic_boost(entry: Dict, query: str) -> float:
    """Calculate semantic similarity boost based on field importance."""
    query_lower = query.lower()
    
    title = entry.get('title', '').lower()
    title_tokens = set(simple_tokenize(title))
    query_tokens = set(simple_tokenize(query))
    title_match = len(title_tokens & query_tokens) / max(1, len(query_tokens))
    
    finding = entry.get('finding', '').lower()
    solution = entry.get('solution', '').lower()
    core_text = f"{finding} {solution}"
    core_tokens = set(simple_tokenize(core_text))
    core_match = len(core_tokens & query_tokens) / max(1, len(query_tokens))
    
    context = entry.get('context', '').lower()
    context_tokens = set(simple_tokenize(context))
    context_match = len(context_tokens & query_tokens) / max(1, len(query_tokens))
    
    semantic_score = 0.5 * title_match + 0.35 * core_match + 0.15 * context_match
    
    return 0.8 + (semantic_score * 0.4)


def get_chroma_client(persist_directory: Optional[Path] = None):
    """Get ChromaDB client with persistence.

    The persist directory is resolved using only relative paths:
    1. Explicit ``persist_directory`` argument (if provided)
    2. Default: ``mcp_servers/knowledge_base/chroma_db`` relative to this file's location
    
    No environment variables are used.
    """
    if persist_directory is None:
        # Always use relative path from this file's location
        persist_directory = Path(__file__).parent.parent / "chroma_db"

    persist_directory.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(persist_directory))
    return client


def get_or_create_collection(client, collection_name: str = "knowledge_base"):
    """Get or create a ChromaDB collection."""
    existing_collections = client.list_collections()
    collection_exists = any(coll.name == collection_name for coll in existing_collections)
    
    if collection_exists:
        collection = client.get_collection(name=collection_name)
    else:
        collection = client.create_collection(
            name=collection_name,
            metadata={
                "description": "Meta Project Harness Knowledge Base",
                "created_at": datetime.now().isoformat()
            }
        )
    
    return collection


_chroma_client = None
_chroma_collection = None

def get_chroma_collection():
    """Get or create global ChromaDB collection."""
    global _chroma_client, _chroma_collection
    
    if _chroma_client is None:
        _chroma_client = get_chroma_client()
    
    if _chroma_collection is None:
        _chroma_collection = get_or_create_collection(_chroma_client)
    
    return _chroma_collection


def hybrid_search_with_chroma(collection, query: str, category: Optional[str] = None, top_k: int = 5) -> List[Dict]:
    """Hybrid search using ChromaDB vector search with metadata filtering."""
    try:
        where_filter = None
        if category:
            where_filter = {"category": category}
        
        results = collection.query(
            query_texts=[query],
            n_results=top_k * 3,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        scored_results = []
        if results and results['ids'] and results['ids'][0]:
            ids = results['ids'][0]
            documents = results['documents'][0] if results['documents'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            distances = results['distances'][0] if results['distances'] else []
            
            for i, doc_id in enumerate(ids):
                if i >= len(documents):
                    continue
                    
                metadata = metadatas[i] if i < len(metadatas) else {}
                distance = distances[i] if i < len(distances) else 1.0
                similarity_score = 1.0 / (1.0 + distance) if distance else 1.0
                doc_text = documents[i]
                kw_score = keyword_score(doc_text, query)
                
                entry = {
                    'id': metadata.get('entry_id', doc_id),
                    'type': metadata.get('type', 'unknown'),
                    'category': metadata.get('category', 'general'),
                    'title': metadata.get('title', doc_id),
                    'confidence': float(metadata.get('confidence', 0.5)),
                    'context': metadata.get('context', ''),
                    'finding': metadata.get('finding', ''),
                    'solution': metadata.get('solution', ''),
                    'example': metadata.get('example', ''),
                    'created_at': metadata.get('created_at', datetime.now().isoformat()),
                }
                
                sem_boost = semantic_boost(entry, query)
                
                try:
                    created = datetime.fromisoformat(entry['created_at'].replace('Z', '+00:00'))
                    days_old = (datetime.now() - created).days
                    recency_bonus = 1.0 / (1.0 + 0.01 * days_old)
                except:
                    recency_bonus = 1.0
                
                title = entry.get('title', '').lower()
                query_lower = query.lower()
                query_tokens = simple_tokenize(query)
                title_match_bonus = 0.0
                
                if query_lower in title:
                    title_match_bonus = 2.0
                elif len([t for t in query_tokens if t in title]) >= 2:
                    title_match_bonus = 1.0
                elif any(token.lower() in title for token in query_tokens):
                    title_match_bonus = 0.5
                
                combined_score = (
                    0.30 * similarity_score +
                    0.20 * kw_score +
                    0.15 * sem_boost +
                    0.15 * entry['confidence'] +
                    0.10 * recency_bonus +
                    0.10 * title_match_bonus
                )
                
                entry['chroma_distance'] = distance
                entry['combined_score'] = combined_score
                
                scored_results.append((combined_score, entry))
        
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [entry for score, entry in scored_results[:top_k]]
    
    except Exception as e:
        print(f"ChromaDB search error: {e}")
        return []


def rag_search(query: str, top_k: int = 5, category: Optional[str] = None) -> Dict[str, Any]:
    """Search knowledge base using ChromaDB."""
    try:
        collection = get_chroma_collection()
        results = hybrid_search_with_chroma(collection, query, category, top_k)
        
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
    """Ask a question and get RAG-augmented response."""
    try:
        collection = get_chroma_collection()
        results = hybrid_search_with_chroma(collection, question, None, top_k)
        
        prompt = """You are an AI agent working on the Agent-X project.
Use the following retrieved knowledge from the project's knowledge base to answer the question.

"""
        if results:
            prompt += "### Retrieved Knowledge:\n\n"
            for i, entry in enumerate(results, 1):
                prompt += f"[{i}] **{entry['title']}** (`{entry['id']}`)\n"
                prompt += f" Type: {entry['type']} | Category: {entry['category']} | Confidence: {entry['confidence']:.2f}\n"
                if entry.get('finding'):
                    prompt += f" Finding: {entry['finding']}\n"
                if entry.get('solution'):
                    prompt += f" Solution: {entry['solution']}\n"
                if entry.get('example'):
                    prompt += f" Example: {entry['example']}\n"
                prompt += "\n"
        else:
            prompt += "No relevant knowledge found in the project knowledge base. Answer based on general knowledge.\n\n"
        
        prompt += f"### Question:\n{question}\n\n### Your Answer:\n"
        
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
                  solution: str, context: str = "", confidence: float = 0.5, 
                  example: str = "") -> Dict[str, Any]:
    """Add new knowledge entry to the knowledge base."""
    try:
        collection = get_chroma_collection()
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        random_val = hash(f"{entry_type}{category}{title}{timestamp}") % 10000
        hash_input = f"{entry_type}{category}{timestamp}{random_val}"
        hash_val = hashlib.md5(hash_input.encode()).hexdigest()[:4].upper()
        prefix_map = {'pattern': 'PAT', 'finding': 'FIND', 'correction': 'COR', 'decision': 'DEC'}
        entry_id = f"{prefix_map.get(entry_type, 'KB')}-{hash_val}"
        
        document_text = f"{title} {finding} {solution} {context} {example}"
        
        metadata = {
            "entry_id": entry_id,
            "type": entry_type,
            "category": category,
            "title": title,
            "finding": finding,
            "solution": solution,
            "context": context,
            "example": example,
            "confidence": confidence,
            "created_at": datetime.now().isoformat(),
        }
        
        collection.add(
            documents=[document_text],
            metadatas=[metadata],
            ids=[entry_id]
        )
        
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


def rag_correct(entry_id: str, reason: str, new_finding: str) -> Dict[str, Any]:
    """Add correction to existing entry (placeholder - needs SQLite for full implementation)."""
    return {
        "success": False,
        "error": "Corrections require SQLite backend",
        "message": "Correction functionality not implemented in ChromaDB-only mode"
    }


def rag_evolve() -> Dict[str, Any]:
    """Run evolution cycle (placeholder)."""
    return {
        "success": False,
        "error": "Evolution requires SQLite backend",
        "message": "Evolution functionality not implemented in ChromaDB-only mode"
    }


def rag_stats() -> Dict[str, Any]:
    """Get knowledge base statistics from ChromaDB."""
    try:
        collection = get_chroma_collection()
        total = collection.count()
        sample = collection.get(limit=1000)
        
        by_type = {}
        by_category = {}
        confidences = []
        
        if sample and "metadatas" in sample and sample["metadatas"]:
            for metadata in sample["metadatas"]:
                if metadata:
                    entry_type = metadata.get("type", "unknown")
                    category = metadata.get("category", "unknown")
                    confidence = metadata.get("confidence", 0.5)
                    by_type[entry_type] = by_type.get(entry_type, 0) + 1
                    by_category[category] = by_category.get(category, 0) + 1
                    confidences.append(confidence)
        
        high = sum(1 for c in confidences if c >= 0.9)
        medium = sum(1 for c in confidences if 0.6 <= c < 0.9)
        low = sum(1 for c in confidences if c < 0.6)
        
        return {
            "success": True,
            "total_entries": total,
            "by_type": {k: {"count": v, "avg_confidence": 0.0} for k, v in by_type.items()},
            "by_category": by_category,
            "confidence_distribution": {"high": high, "medium": medium, "low": low},
            "pending_corrections": 0
        }
    except Exception as e:
        return {"success": False, "error": str(e), "message": f"Stats failed: {str(e)}"}


# Aliases for backward compatibility
chroma_rag_search = rag_search
chroma_rag_ask = rag_ask
chroma_rag_add_entry = rag_add_entry
chroma_rag_correct = rag_correct
chroma_rag_evolve = rag_evolve
chroma_rag_stats = rag_stats

__all__ = [
    "rag_search", "rag_ask", "rag_add_entry", "rag_correct", "rag_evolve", "rag_stats",
    "simple_tokenize", "escape_fts5_query", "keyword_score", "semantic_boost",
    "get_chroma_collection", "hybrid_search_with_chroma"
]
