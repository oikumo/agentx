"""Wave 1 / P1-1 think-batch-consult — feature_066.

Contract (GREEN pins the implementation):
- BATCH: omt_think{op:list, path:[...]} consults multiple files/dirs in ONE op —
  a single think_consult ledger record carries the union files[] (set
  semantics), clearing g.think for every matched file (same session).
- QUERY-SCOPED: category:/query: filters already narrow the matched set — the
  record covers only shown files (safe direction); empty result covers nothing.
- RISK STAYS PER-FILE: hasConsultedThoughts drops the cross-session window for
  risk:-carrying files — a risk file demands THIS session looked (batch in the
  same session still clears when included; an old batch never clears risk).

Bun probes exercise the REAL TS modules (feature_063 idiom): hermetic ledger
via OMT_LEDGER_PATH for think_gate.hasConsultedThoughts set-semantics + risk.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent.parent
THINK_PLUGIN = REPO_ROOT / ".opencode" / "plugins" / "omt_think.ts"
THINK_GATE = REPO_ROOT / ".opencode" / "lib" / "enforcer" / "think_gate.ts"

BUN = shutil.which("bun")

F = "feature_066.think_batch_consult"


def _ts(hours_ago: float = 0.0) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).isoformat()


def _consult(session: str = "s1", files: list[str] | None = None,
             hours_ago: float = 0.0) -> dict:
    return {"ts": _ts(hours_ago), "kind": "think_consult", "session": session,
            "files": files if files is not None else []}


def _run_probe(tmp_path: Path, body: str) -> dict:
    """Write body to tmp/probe.ts, run bun with a hermetic ledger env."""
    assert BUN is not None, "bun runtime required (guard against skipif bypass)"
    ledger = tmp_path / "ledger.jsonl"
    probe = tmp_path / "probe.ts"
    probe.write_text(body, encoding="utf-8")
    env = {**os.environ, "OMT_LEDGER_PATH": str(ledger)}
    out = subprocess.run([BUN, str(probe)], capture_output=True, text=True,
                         timeout=90, cwd=str(tmp_path), env=env)
    assert out.returncode == 0, f"bun probe failed:\n{out.stderr}\n---"
    return json.loads(out.stdout.strip().splitlines()[-1])


# --- static pins (P1-1 wiring) -------------------------------------------------

class TestStaticPins:
    def test_static_batch_path_array(self) -> None:
        src = THINK_PLUGIN.read_text(encoding="utf-8")
        assert "Array.isArray(pathArg)" in src, (
            "P1-1 requires path:string|string[] handling in omt_think_list "
            "(SDK coerces JSON-array strings to real arrays)")
        assert "targets" in src and "grepThoughts(pattern, target)" in src, (
            "batch must loop grepThoughts per target and union hits")

    def test_static_single_record_dedup(self) -> None:
        src = THINK_PLUGIN.read_text(encoding="utf-8")
        assert "new Set<string>()" in src or "new Set" in src, (
            "batch must dedup hits across overlapping targets")
        # one recordConsult per LIST op (review also consults by design,
        # feature_058 — scope the count to the list block).
        list_block = src.split("const omt_think_list")[1].split(
            "const omt_think_remove")[0]
        assert list_block.count("recordConsult(session, consultedFiles)") == 1, (
            "batch must write ONE think_consult record per list op")

    def test_static_risk_stays_per_file(self) -> None:
        gate = THINK_GATE.read_text(encoding="utf-8")
        assert "if (opts?.risk) return false" in gate, (
            "P1-1 MUST NOT weaken risk: cross-session window stays dropped "
            "for risk-carrying files (same-session batch still clears)")


# --- probe A: hasConsultedThoughts set-semantics + risk (real module) ----------

_A_PROBE = """
import { writeFileSync } from "node:fs"
import { hasConsultedThoughts } from "%TG%"
const ledger = process.env.OMT_LEDGER_PATH!
const cases: Record<string, { recs: any[]; rel: string; risk?: boolean; session?: string }> = %CASES%
const out: Record<string, boolean> = {}
for (const [name, c] of Object.entries(cases)) {
  writeFileSync(ledger, c.recs.map((r: any) => JSON.stringify(r)).join("\\n") + "\\n")
  out[name] = hasConsultedThoughts(c.session ?? "s1", c.rel, { risk: c.risk })
}
console.log(JSON.stringify(out))
"""


class TestBatchConsultSemanticsBun:
    @classmethod
    def _cases(cls) -> dict:
        batch = [_consult("s1", ["a.py", "b.py", "c.py"])]
        return {
            # one batch record clears every member file in the same session
            "batch_clears_a": {"recs": batch, "rel": "a.py"},
            "batch_clears_b": {"recs": batch, "rel": "b.py"},
            "batch_clears_c": {"recs": batch, "rel": "c.py"},
            # non-member file stays blocked
            "batch_misses_d": {"recs": batch, "rel": "d.py"},
            # empty-result record covers nothing
            "empty_covers_nothing": {"recs": [_consult("s1", [])],
                                     "rel": "a.py"},
            # cross-session window: non-risk covered, risk dropped (per-file)
            "window_clears_nonrisk": {"recs": [_consult("s9", ["a.py"],
                                                        hours_ago=1)],
                                      "rel": "a.py", "session": "s1"},
            "window_drops_risk": {"recs": [_consult("s9", ["a.py"],
                                                    hours_ago=1)],
                                  "rel": "a.py", "session": "s1",
                                  "risk": True},
            # same-session batch DOES clear risk when included
            "batch_clears_risk_same_session": {"recs": batch, "rel": "a.py",
                                               "risk": True},
        }

    def test_bun_batch_set_semantics_and_risk(self, tmp_path) -> None:
        if BUN is None:
            import pytest
            pytest.skip("bun runtime not available")
        out = _run_probe(tmp_path, _A_PROBE
                         .replace("%TG%", str(THINK_GATE))
                         .replace("%CASES%", json.dumps(self._cases())))
        assert out == {
            "batch_clears_a": True, "batch_clears_b": True,
            "batch_clears_c": True, "batch_misses_d": False,
            "empty_covers_nothing": False,
            "window_clears_nonrisk": True, "window_drops_risk": False,
            "batch_clears_risk_same_session": True,
        }, f"batch consult semantics mismatch: {out}"
