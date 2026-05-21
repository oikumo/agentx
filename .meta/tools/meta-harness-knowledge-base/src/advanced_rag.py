#!/usr/bin/env python3
"""
Advanced RAG System with ChromaDB
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from rag_tool import get_chroma_collection, simple_tokenize, keyword_score, semantic_boost


class ChromaDBAdvancedRAG:
    """Advanced RAG system with ChromaDB backend."""
    
    def __init__(self):
        self.collection = get_chroma_collection()
    
    def rewrite_query(self, query: str) -> List[str]:
        """Expand query into multiple variations."""
        variations = [query]
        tokens = simple_tokenize(query)
        keywords = [t for t in tokens if len(t) > 3]
        
        if keywords:
            variations.append(" ".join(keywords))
            variations.extend(keywords)
            
            for connector in [" and ", " or ", " how ", " what ", " where "]:
                if connector in query.lower():
                    parts = re.split(rf'\b{connector.strip()}\b', query, flags=re.IGNORECASE)
                    variations.extend([p.strip() for p in parts if len(p.strip()) > 5])
            
            statement = re.sub(r'\b(what|where|when|how|why|which|who)\b\s*', '', query, flags=re.IGNORECASE)
            if statement.strip():
                variations.append(statement.strip())
        
        seen = set()
        unique_variations = []
        for v in variations:
            v_lower = v.lower().strip()
            if v_lower and v_lower not in seen:
                seen.add(v_lower)
                unique_variations.append(v)
        
        return unique_variations[:10]
    
    def _search(self, query: str, top_k: int = 5, category: Optional[str] = None) -> List[Dict]:
        """Internal search method."""
        try:
            where_filter = None
            if category:
                where_filter = {"category": category}
            
            results = self.collection.query(
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
                    
                    entry['combined_score'] = combined_score
                    scored_results.append((combined_score, entry))
            
            scored_results.sort(key=lambda x: x[0], reverse=True)
            return [entry for score, entry in scored_results[:top_k]]
        
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def advanced_search(self, query: str, top_k: int = 5,
                       use_multi_hop: bool = True,
                       use_diversification: bool = True,
                       category: Optional[str] = None) -> Dict[str, Any]:
        """Advanced search with query expansion."""
        start_time = datetime.now()
        
        query_variations = self.rewrite_query(query)
        
        query_lower = query.lower()
        is_simple_lookup = any(pattern in query_lower for pattern in ['what is', 'what are', 'who is', 'class:', 'method:', 'function:'])
        effective_multi_hop = use_multi_hop and len(query.split()) > 3 and not is_simple_lookup
        
        if effective_multi_hop:
            all_results = []
            seen_ids = set()
            
            current_query = query
            for hop in range(2):
                results = self._search(current_query, top_k * 2, category)
                for r in results:
                    if r['id'] not in seen_ids:
                        seen_ids.add(r['id'])
                        r['hop'] = hop
                        all_results.append(r)
                
                if results and len(results) > 0:
                    top_result = results[0]
                    combined_text = f"{top_result['title']} {top_result['finding']} {top_result['solution']}"
                    next_query_terms = simple_tokenize(combined_text)[:5]
                    current_query = " ".join(next_query_terms)
                else:
                    break
            
            results = all_results
        else:
            results = self._search(query, top_k * 2, category)
        
        if use_diversification and len(results) > 2:
            by_category = defaultdict(list)
            for r in results:
                by_category[r.get('category', 'other')].append(r)
            
            diversified = []
            for cat in by_category:
                if by_category[cat]:
                    diversified.append(by_category[cat][0])
            
            remaining = len(results) - len(diversified)
            if remaining > 0:
                existing_ids = {r['id'] for r in diversified}
                for r in results:
                    if r['id'] not in existing_ids:
                        diversified.append(r)
                        remaining -= 1
                    if remaining == 0:
                        break
            
            results = diversified
        
        results = results[:top_k]
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
        """Ask a question with advanced RAG."""
        if use_advanced:
            search_result = self.advanced_search(question, top_k)
            results = search_result['results']
        else:
            results = self._search(question, top_k)
        
        if synthesize:
            return self._synthesize_answer(question, results)
        else:
            return {
                "success": True,
                "question": question,
                "context": results,
                "count": len(results)
            }
    
    def _synthesize_answer(self, question: str, results: List[Dict]) -> Dict[str, Any]:
        """Synthesize answer from results."""
        if not results:
            return {
                "success": True,
                "answer": "No relevant information found in the knowledge base.",
                "sources": [],
                "confidence": 0.0
            }
        
        answer_parts = []
        sources = []
        total_confidence = 0.0
        
        by_type = defaultdict(list)
        for r in results:
            by_type[r['type']].append(r)
        
        for entry_type in ['pattern', 'finding', 'decision', 'correction']:
            if entry_type in by_type:
                type_results = by_type[entry_type]
                answer_parts.append(f"\n## {entry_type.title()}s Found: {len(type_results)}")
                
                for i, r in enumerate(type_results[:3], 1):
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
        
        avg_confidence = total_confidence / len(sources) if sources else 0.0
        
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


# Convenience functions
def advanced_search(query: str, top_k: int = 5, **kwargs) -> Dict[str, Any]:
    """Convenience function for advanced search."""
    rag = ChromaDBAdvancedRAG()
    return rag.advanced_search(query, top_k, **kwargs)


def advanced_ask(question: str, top_k: int = 5, **kwargs) -> Dict[str, Any]:
    """Convenience function for advanced ask."""
    rag = ChromaDBAdvancedRAG()
    return rag.ask(question, top_k, **kwargs)
