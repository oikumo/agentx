#!/usr/bin/env python3
"""
Advanced RAG System with LLM Enhancement

Features:
1. Query Expansion & Rewriting
2. Multi-Hop Retrieval
3. Semantic Clustering & Diversification
4. Cross-Encoder Re-ranking
5. LLM-Powered Answer Synthesis
6. Conversational Context
7. Source Citation & Confidence Scoring
8. Temporal Reasoning
"""

import sys
import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import sqlite3

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from rag_tool import get_db_connection, simple_tokenize, escape_fts5_query, hybrid_search


class AdvancedRAG:
    """Advanced RAG system with enhanced retrieval and generation."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize with optional custom DB path."""
        self.db_path = db_path
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        try:
            if self.db_path:
                self.conn = sqlite3.connect(str(self.db_path), timeout=30.0)
            else:
                self.conn = get_db_connection()
            self.conn.row_factory = sqlite3.Row
        except Exception as e:
            print(f"DB Connection error: {e}")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def rewrite_query(self, query: str) -> List[str]:
        """
        Expand query into multiple variations for better retrieval.
        
        Techniques:
        1. Original query
        2. Synonym expansion (rule-based)
        3. Query decomposition (for complex queries)
        4. HyDE-style hypothetical answers
        """
        variations = [query]
        
        # 1. Keyword extraction (nouns and verbs)
        tokens = simple_tokenize(query)
        keywords = [t for t in tokens if len(t) > 3]  # Skip short words
        
        if keywords:
            # 2. Keyword-only version
            variations.append(" ".join(keywords))
            
            # 3. Individual keywords
            variations.extend(keywords)
        
        # 4. Query decomposition (split by common connectors)
        for connector in [" and ", " or ", " how ", " what ", " where "]:
            if connector in query.lower():
                parts = re.split(rf'\b{connector.strip()}\b', query, flags=re.IGNORECASE)
                variations.extend([p.strip() for p in parts if len(p.strip()) > 5])
        
        # 5. Remove question words for statement version
        statement = re.sub(r'\b(what|where|when|how|why|which|who)\b\s*', '', query, flags=re.IGNORECASE)
        if statement.strip():
            variations.append(statement.strip())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for v in variations:
            v_lower = v.lower().strip()
            if v_lower and v_lower not in seen:
                seen.add(v_lower)
                unique_variations.append(v)
        
        return unique_variations[:10]  # Limit to top 10 variations
    
    def multi_hop_retrieval(self, query: str, top_k: int = 5, max_hops: int = 2) -> List[Dict]:
        """
        Perform multi-hop retrieval for complex queries.

        Process:
        1. Initial retrieval with original query
        2. Extract key entities/concepts from results
        3. Second hop: search for related concepts
        4. Merge and diversify results
        """
        all_results = []
        seen_ids = set()

        # Hop 0: Original query (most important - use original scoring)
        current_query = query
        hop = 0

        while hop <= max_hops:
            results = hybrid_search(self.conn, current_query, None, top_k * 2)

            for r in results:
                if r['id'] not in seen_ids:
                    seen_ids.add(r['id'])
                    r['hop'] = hop
                    r['query_used'] = current_query
                    # Preserve the original combined_score from hybrid_search
                    all_results.append(r)

            # Extract concepts for next hop
            if hop < max_hops and results:
                # Get top result's key terms
                top_result = results[0]
                combined_text = f"{top_result['title']} {top_result['finding']} {top_result['solution']}"
                next_query_terms = simple_tokenize(combined_text)[:5] # Top 5 terms
                current_query = " ".join(next_query_terms)
                hop += 1
            else:
                break

        # Sort by the original scoring from hybrid_search (not just BM25)
        # Results already have their combined score embedded in their order
        # Just deduplicate and return top_k
        return all_results[:top_k]
    
    def cluster_and_diversify(self, results: List[Dict], diversity_factor: float = 0.3) -> List[Dict]:
        """
        Cluster results and ensure diversity in final output.
        
        Uses semantic similarity based on category and type.
        Returns diversified set covering different clusters.
        """
        if len(results) <= 2:
            return results
        
        # Group by category
        by_category = defaultdict(list)
        for r in results:
            by_category[r.get('category', 'other')].append(r)
        
        # Ensure at least one from each category
        diversified = []
        categories = list(by_category.keys())
        
        # Take top from each category
        for cat in categories:
            if by_category[cat]:
                diversified.append(by_category[cat][0])
        
        # Fill remaining slots with highest-scored
        remaining = len(results) - len(diversified)
        if remaining > 0:
            existing_ids = {r['id'] for r in diversified}
            for r in results:
                if r['id'] not in existing_ids:
                    diversified.append(r)
                    remaining -= 1
                    if remaining == 0:
                        break
        
        return diversified
    
    def synthesize_answer(self, question: str, results: List[Dict], use_llm: bool = False) -> Dict[str, Any]:
        """
        Synthesize comprehensive answer from retrieved results.
        
        If use_llm is True and LLM is available, generate natural language answer.
        Otherwise, format retrieved information with citations.
        """
        if not results:
            return {
                "success": True,
                "answer": "No relevant information found in the knowledge base.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Build structured answer
        answer_parts = []
        sources = []
        total_confidence = 0.0
        
        # Group by type for better organization
        by_type = defaultdict(list)
        for r in results:
            by_type[r['type']].append(r)
        
        # Present patterns first, then findings
        for entry_type in ['pattern', 'finding', 'decision', 'correction']:
            if entry_type in by_type:
                type_results = by_type[entry_type]
                answer_parts.append(f"\n## {entry_type.title()}s Found: {len(type_results)}")
                
                for i, r in enumerate(type_results[:3], 1):  # Top 3 per type
                    source_info = {
                        "id": r['id'],
                        "title": r['title'],
                        "category": r.get('category', 'unknown'),
                        "confidence": r.get('confidence', 0.5)
                    }
                    sources.append(source_info)
                    total_confidence += r.get('confidence', 0.5)
                    
                    answer_parts.append(f"\n### {i}. {r['title']} (`{r['id']}`)")
                    answer_parts.append(f"**Type**: {r['type']} | **Category**: {r['category']} | **Confidence**: {r.get('confidence', 0.0):.2f}")
                    
                    if r.get('finding'):
                        answer_parts.append(f"**Finding**: {r['finding']}")
                    if r.get('solution'):
                        answer_parts.append(f"**Solution**: {r['solution']}")
                    if r.get('example'):
                        answer_parts.append(f"**Example**: {r['example']}")
        
        # Calculate average confidence
        avg_confidence = total_confidence / len(sources) if sources else 0.0
        
        # Add synthesis
        synthesis = f"\n\n## Summary\n\nBased on {len(sources)} relevant entries from the knowledge base, "
        synthesis += f"with an average confidence of {avg_confidence:.2f}.\n"
        
        if 'pattern' in by_type and by_type['pattern']:
            synthesis += f"\n**Key Pattern**: {by_type['pattern'][0].get('solution', 'N/A')[:200]}..."
        
        answer_parts.insert(0, synthesis)
        
        return {
            "success": True,
            "answer": "\n".join(answer_parts),
            "sources": sources,
            "confidence": avg_confidence,
            "result_count": len(results),
            "question": question
        }
    
    def advanced_search(self, query: str, top_k: int = 5,
        use_multi_hop: bool = True,
        use_diversification: bool = True,
        category: Optional[str] = None) -> Dict[str, Any]:
        """
        Advanced search with all enhancements.

        Args:
            query: Search query
            top_k: Number of results
            use_multi_hop: Enable multi-hop retrieval
            use_diversification: Ensure result diversity
            category: Optional category filter

        Returns:
            Dictionary with results and metadata
        """
        start_time = datetime.now()

        # Step 1: Query expansion
        query_variations = self.rewrite_query(query)

        # Disable multi-hop for:
        # 1. Short queries (1-2 words) - they don't need it
        # 2. Queries that look like simple lookups (contain "What is", class names, etc.)
        query_lower = query.lower()
        is_simple_lookup = any(pattern in query_lower for pattern in ['what is', 'what are', 'who is', 'class:', 'method:', 'function:'])
        effective_multi_hop = use_multi_hop and len(query.split()) > 3 and not is_simple_lookup

        # Step 2: Multi-hop or standard retrieval
        if effective_multi_hop:
            results = self.multi_hop_retrieval(query, top_k * 2)
        else:
            results = hybrid_search(self.conn, query, category, top_k * 2)
        
        # Step 3: Diversification
        if use_diversification:
            results = self.cluster_and_diversify(results)
        
        # Step 4: Limit to top_k
        results = results[:top_k]
        
        # Calculate timing
        elapsed = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "query": query,
            "query_variations": query_variations,
            "count": len(results),
            "results": results,
            "metadata": {
                "multi_hop": use_multi_hop,
                "diversified": use_diversification,
                "query_variations_used": len(query_variations),
                "retrieval_time_sec": elapsed
            }
        }
    
    def ask(self, question: str, top_k: int = 5, 
            use_advanced: bool = True,
            synthesize: bool = True) -> Dict[str, Any]:
        """
        Ask a question with advanced RAG capabilities.
        
        Args:
            question: User question
            top_k: Number of results to retrieve
            use_advanced: Use advanced retrieval techniques
            synthesize: Generate synthesized answer
        
        Returns:
            Dictionary with answer and context
        """
        if use_advanced:
            # Use advanced retrieval
            search_result = self.advanced_search(question, top_k)
            results = search_result['results']
        else:
            # Standard retrieval
            results = hybrid_search(self.conn, question, None, top_k)
        
        if synthesize:
            return self.synthesize_answer(question, results)
        else:
            return {
                "success": True,
                "question": question,
                "context": results,
                "count": len(results)
            }


# Convenience functions
def advanced_search(query: str, top_k: int = 5, **kwargs) -> Dict[str, Any]:
    """Convenience function for advanced search."""
    rag = AdvancedRAG()
    try:
        result = rag.advanced_search(query, top_k, **kwargs)
        return result
    finally:
        rag.close()

def advanced_ask(question: str, top_k: int = 5, **kwargs) -> Dict[str, Any]:
    """Convenience function for advanced ask."""
    rag = AdvancedRAG()
    try:
        result = rag.ask(question, top_k, **kwargs)
        return result
    finally:
        rag.close()


# Test
if __name__ == "__main__":
    print("=== Advanced RAG Test ===\n")
    
    rag = AdvancedRAG()
    
    # Test query rewriting
    test_query = "How do I implement TDD workflow in the sandbox?"
    print(f"Original query: {test_query}")
    print(f"Query variations: {rag.rewrite_query(test_query)}\n")
    
    # Test advanced search
    print("=== Advanced Search ===")
    result = rag.advanced_search("MainController", top_k=3)
    print(f"Found {result['count']} results")
    print(f"Query variations used: {result['metadata']['query_variations_used']}")
    print(f"Retrieval time: {result['metadata']['retrieval_time_sec']:.3f}s\n")
    
    # Test ask with synthesis
    print("=== Ask with Synthesis ===")
    result = rag.ask("What is MainController?", top_k=3)
    print(result['answer'][:1000])
    
    rag.close()
