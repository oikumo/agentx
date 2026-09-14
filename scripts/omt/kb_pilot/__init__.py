"""T3-6 pilot (feature_094, option A): selective verifiable knowledge.

Read-only advisory layer over a sidecar of lesson metadata. It NEVER blocks,
grants, or mutates policy — lookup returns advisory pointers (id/title/evidence)
for a change surface (files/symbols, incl. dependents). Promotion/retirement are
pure record transitions with a documented reason + replacement check.

Scope: top repeated-discovery lessons ONLY (3 seeded). No auto-learning path.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

LESSONS_PATH = Path(__file__).with_name("lessons.json")

REQUIRED_FIELDS = (
    "id",
    "title",
    "symbols",
    "files",
    "dependents",
    "evidence_test",
    "content_version",
    "expiry",
    "status",
)

ADVISORY_KEYS = ("id", "title", "evidence_test", "expiry", "matched_on")


def load_lessons(path: str | Path | None = None) -> dict:
    """Load the sidecar doc. Raises on missing file / bad shape."""
    doc = json.loads(Path(path or LESSONS_PATH).read_text(encoding="utf-8"))
    assert isinstance(doc.get("lessons"), list), "sidecar needs a lessons list"
    for lesson in doc["lessons"]:
        missing = [f for f in REQUIRED_FIELDS if f not in lesson]
        assert not missing, f"lesson {lesson.get('id', '?')} missing {missing}"
    return doc


def active_lessons(doc: dict) -> list[dict]:
    """Lessons with status == active (promoted/retired are lifecycle-closed)."""
    return [lesson for lesson in doc["lessons"] if lesson.get("status") == "active"]


def lookup(
    doc: dict,
    changed_files: list[str] | tuple[str, ...] = (),
    changed_symbols: list[str] | tuple[str, ...] = (),
) -> list[dict]:
    """Advisory retrieval for a change surface. Pure: no side effects.

    Matches active lessons whose files/dependents intersect changed_files or
    whose symbols intersect changed_symbols. Unrelated surfaces return [] —
    no re-consult required.
    """
    files = set(changed_files or ())
    symbols = set(changed_symbols or ())
    if not files and not symbols:
        return []
    advisories = []
    for lesson in active_lessons(doc):
        matched: list[str] = []
        hit_files = files & set(lesson.get("files", []))
        hit_deps = files & set(lesson.get("dependents", []))
        hit_syms = symbols & set(lesson.get("symbols", []))
        matched += [f"file:{f}" for f in sorted(hit_files)]
        matched += [f"dependent:{f}" for f in sorted(hit_deps)]
        matched += [f"symbol:{s}" for s in sorted(hit_syms)]
        if matched:
            advisories.append(
                {
                    "id": lesson["id"],
                    "title": lesson["title"],
                    "evidence_test": lesson["evidence_test"],
                    "expiry": lesson["expiry"],
                    "matched_on": matched,
                }
            )
    return advisories


def needs_refresh(lesson: dict, current_version: str) -> bool:
    """True when the lesson's recorded content_version differs from current."""
    return lesson.get("content_version") != current_version


def promote(lesson: dict, check_ref: str, reason: str) -> dict:
    """Promote a hot testable lesson to a check. Returns a NEW record.

    The prose record closes with status=promoted, the replacement check ref,
    and the documented reason — the original dict is never mutated.
    """
    updated = copy.deepcopy(lesson)
    updated["status"] = "promoted"
    updated["replacement_check"] = check_ref
    updated["retire_reason"] = reason
    return updated


def retire(lesson: dict, reason: str) -> dict:
    """Retire an obsolete lesson with a documented reason. Returns NEW record."""
    updated = copy.deepcopy(lesson)
    updated["status"] = "retired"
    updated["retire_reason"] = reason
    return updated
