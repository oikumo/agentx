"""Answer synthesis from retrieved knowledge-base entries.

Replaces the dead `advanced_rag._synthesize_answer` and the prompt-template
behaviour of `rag_tool.rag_ask` (Plan P4). Multi-hop and query rewriting are
deliberately dropped until proven needed.
"""

from collections import defaultdict
from typing import Dict, List

from .models import AskResult, AskSource


_TYPE_ORDER = ("pattern", "finding", "decision", "correction")
_MAX_PER_TYPE = 3


def synthesize(question: str, results: List[Dict]) -> AskResult:
    """Build a markdown answer + sources list from raw search results.

    Args:
        question: the original user question (echoed for context, not required).
        results: list of result dicts as produced by `kb.search.hybrid_search`.

    Returns:
        An `AskResult` with a markdown answer, citation sources, and the
        average confidence across the cited entries.
    """
    if not results:
        return AskResult(
            success=True,
            answer="No relevant information found in the knowledge base.",
            sources=[],
            confidence=0.0,
        )

    by_type: Dict[str, List[Dict]] = defaultdict(list)
    for r in results:
        by_type[r.get("type", "unknown")].append(r)

    body_parts: List[str] = []
    sources: List[AskSource] = []
    total_confidence = 0.0

    for entry_type in _TYPE_ORDER:
        if entry_type not in by_type:
            continue
        type_results = by_type[entry_type]
        body_parts.append(f"\n## {entry_type.title()}s Found: {len(type_results)}")

        for i, r in enumerate(type_results[:_MAX_PER_TYPE], 1):
            conf = float(r.get("confidence", 0.5))
            sources.append(AskSource(
                id=r.get("id", "unknown"),
                title=r.get("title", "(untitled)"),
                type=r.get("type", entry_type),
                category=r.get("category", "unknown"),
                confidence=conf,
            ))
            total_confidence += conf

            body_parts.append(f"\n### {i}. {r.get('title', '(untitled)')} (`{r.get('id', '?')}`)")
            body_parts.append(
                f"**Type**: {r.get('type', entry_type)} | "
                f"**Category**: {r.get('category', 'unknown')} | "
                f"**Confidence**: {conf:.2f}"
            )
            if r.get("finding"):
                body_parts.append(f"**Finding**: {r['finding']}")
            if r.get("solution"):
                body_parts.append(f"**Solution**: {r['solution']}")
            if r.get("example"):
                body_parts.append(f"**Example**: {r['example']}")

    avg_confidence = total_confidence / len(sources) if sources else 0.0

    summary = (
        f"\n\n## Summary\n\n"
        f"Based on {len(sources)} relevant entries from the knowledge base, "
        f"with an average confidence of {avg_confidence:.2f}.\n"
    )
    if by_type.get("pattern"):
        first_pattern_solution = by_type["pattern"][0].get("solution", "")
        if first_pattern_solution:
            summary += f"\n**Key Pattern**: {first_pattern_solution[:200]}..."

    answer = summary + "\n" + "\n".join(body_parts)

    return AskResult(
        success=True,
        answer=answer,
        sources=sources,
        confidence=avg_confidence,
    )
