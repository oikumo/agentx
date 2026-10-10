"""test_argv_value_guard_pins.py — cross-source pin (feature_136).

Every plugin argv/flag push site must serialize values through the shared
argvValue() helper (.opencode/lib/omt_shared.ts) so SDK-coerced arrays AND
objects re-serialize to valid JSON. The object half was diagnosed live in the
mh14 run001 trial (2026-09-27): omt_session query_json '{"limit": 3}' arrived
as a JS object; String(v) produced '[object Object]'; session_inspect
json.loads threw "Expecting value: line 1 column 2 (char 1)". The array half
was feature_027 (2026-08-15, tdd behaviors). Drift here re-opens the
"[object Object]" class at tool boundaries (experiment collect passes
manifest/selection_json through the same path).
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

SHARED = ".opencode/lib/omt_shared.ts"
SITES = [
    ".opencode/plugins/omt_session.ts",      # query_json/manifest/selection_json (collect path)
    ".opencode/plugins/omt_net.ts",           # splice/synthesize/mine mutation
    ".opencode/lib/enforcer/tdd_hats.ts",    # testlist behaviors
    ".opencode/plugins/reason_check.ts",     # concretize row (JSON)
]


def _text(rel: str) -> str:
    return (REPO / rel).read_text()


def test_shared_helper_exists_with_object_guard():
    """argvValue must live in omt_shared.ts and guard BOTH shapes (arrays are
    typeof "object" too — one guard covers both)."""
    shared = _text(SHARED)
    assert "export function argvValue(v: unknown): string" in shared, "argvValue helper missing"
    assert 'if (v !== null && typeof v === "object") return JSON.stringify(v)' in shared, (
        "object-shape guard missing in argvValue"
    )
    assert "return String(v)" in shared, "scalar passthrough missing in argvValue"


def _code_only(rel: str) -> str:
    """Strip TA: thought lines — pins target live code, not historical prose
    (tdd_hats.ts:48's gotcha legitimately quotes the old ternary)."""
    return "\n".join(l for l in _text(rel).splitlines() if "TA:" not in l)


def test_every_push_site_uses_argv_value():
    for rel in SITES:
        text = _code_only(rel)
        assert re.search(r"import \{[^}]*argvValue[^}]*\} from", text), (
            f"argvValue import missing in {rel}"
        )
        assert "argvValue(v))" in text, f"argvValue(v) call missing in {rel}"
        assert "Array.isArray(v) ? JSON.stringify(v) : String(v)" not in text, (
            f"stale array-only ternary still present in {rel}"
        )
        assert "String(v))" not in text, (
            f"bare String(v) argv push still present in {rel}"
        )


def test_ta_gotcha_recorded_at_helper():
    """The class doc must stay attached to the helper (think-gate surface)."""
    shared = _text(SHARED)
    assert re.search(r"TA: gotcha:.*argvValue", shared) or "argvValue" in shared.split("TA: gotcha:")[1], (
        "feature_136 TA: gotcha missing near argvValue"
    )
