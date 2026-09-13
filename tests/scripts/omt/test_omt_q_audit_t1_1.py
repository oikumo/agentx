"""Golden tests for T1-1 ordered skip audit + bootstrap fingerprint (feature_086).

Acceptance (PROJECT.md T1-1):
- omt_q{op:audit} returns skip_audit in ledger file order + scope_tally.
- bootstrap_templates returns the last-3 skip reasons matching /bootstrap/i;
  with `feature`, only reasons containing the feature substring qualify.

Probes exercise the real TS plugin via bun (same pattern as test_omt_q_audit.py).
"""
from __future__ import annotations

import glob
import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
OMT_Q_PLUGIN = REPO_ROOT / ".opencode" / "plugins" / "omt_q.ts"
SHARED_LIB = REPO_ROOT / ".opencode" / "lib" / "omt_shared.ts"

BUN = shutil.which("bun")

_q_probe_template = """
import { initOmtShared, repoRoot } from "%LIB%"
initOmtShared(process.argv[2])
const mod = await import("%PLUGIN%")
const { tool } = await mod.default({ directory: process.argv[2], worktree: process.argv[2] })
const args = %ARGS%
const result = await tool.omt_q.execute(args, { sessionID: "%SESSION%" })
console.log(result)
"""


def _q_probe(args_str: str, session: str = "ses_t1_1", tmp_path: Path | None = None,
             use_real_root: bool = False) -> dict:
    assert BUN is not None, "bun required"
    assert tmp_path is not None
    root = REPO_ROOT if use_real_root else tmp_path
    probe = tmp_path / "probe_t1_1.ts"
    probe.write_text(
        _q_probe_template
        .replace("%LIB%", str(SHARED_LIB))
        .replace("%PLUGIN%", str(OMT_Q_PLUGIN))
        .replace("%ARGS%", args_str)
        .replace("%SESSION%", session),
        encoding="utf-8",
    )
    out = subprocess.run([BUN, str(probe), str(root)],
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, f"bun probe failed:\n{out.stderr}\n---"
    return json.loads(out.stdout.strip().splitlines()[-1])


def _read_all_ledger() -> list:
    recs = []
    for fn in sorted(glob.glob(str(REPO_ROOT / ".meta" / ".omt" / "ledger-*.jsonl"))):
        for line in Path(fn).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    for line in (REPO_ROOT / ".meta" / ".omt" / "ledger.jsonl").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            recs.append(json.loads(line))
    return recs


def _seed_ledger(tmp_path: Path, records: list) -> None:
    dst = tmp_path / ".meta" / ".omt"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO_ROOT / ".meta" / ".omt" / "harness.ir.json",
                 dst / "harness.ir.json")
    with (dst / "ledger.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


class TestOrderedSkipAudit:
    @pytest.mark.skipif(BUN is None, reason="bun not available")
    def test_ordered_audit_matches_ledger_order_live(self, tmp_path, monkeypatch):
        monkeypatch.delenv("OMT_LEDGER_PATH", raising=False)
        out = _q_probe(json.dumps({"op": "audit"}), tmp_path=tmp_path,
                       use_real_root=True)
        assert out["op"] == "audit"
        skips = [r for r in _read_all_ledger() if r.get("kind") == "skip"]
        assert len(skips) > 0, "expected live skip records"
        audit = out.get("skip_audit", [])
        assert [e.get("ts") for e in audit] == [r.get("ts") for r in skips], \
            "skip_audit order must match ledger file order"
        tally = out.get("scope_tally", {})
        assert sum(tally.values()) == len(skips)
        assert tally == dict(Counter(r.get("scope", "") for r in skips))

    @pytest.mark.skipif(BUN is None, reason="bun not available")
    def test_bootstrap_templates_last_three_live(self, tmp_path, monkeypatch):
        monkeypatch.delenv("OMT_LEDGER_PATH", raising=False)
        out = _q_probe(json.dumps({"op": "audit"}), tmp_path=tmp_path,
                       use_real_root=True)
        boots = [r.get("reason", "") for r in _read_all_ledger()
                 if r.get("kind") == "skip" and "bootstrap" in (r.get("reason") or "").lower()]
        assert len(boots) >= 3, "expected ≥3 live bootstrap skip reasons"
        assert out.get("bootstrap_templates") == boots[-3:]

    @pytest.mark.skipif(BUN is None, reason="bun not available")
    def test_hermetic_seeded_order_and_feature_filter(self, tmp_path, monkeypatch):
        monkeypatch.delenv("OMT_LEDGER_PATH", raising=False)
        seed = [
            {"ts": "2026-01-01T00:00:00.000Z", "kind": "skip", "session": "s1",
             "scope": "tests", "reason": "TDD bootstrap: create RED file for feature_900.alpha"},
            {"ts": "2026-01-02T00:00:00.000Z", "kind": "phase", "session": "s1",
             "feature": "feature_900.alpha", "phase": "Analysis", "task_type": "minor_feature",
             "scope": "seed"},
            {"ts": "2026-01-03T00:00:00.000Z", "kind": "skip", "session": "s1",
             "scope": "nav", "reason": "live smoke"},
            {"ts": "2026-01-04T00:00:00.000Z", "kind": "skip", "session": "s2",
             "scope": "tests", "reason": "TDD_BOOTSTRAP: first tests/ write for feature_901.beta"},
            {"ts": "2026-01-05T00:00:00.000Z", "kind": "skip", "session": "s2",
             "scope": "tests", "reason": "approved canary test — hermetic seed"},
            {"ts": "2026-01-06T00:00:00.000Z", "kind": "skip", "session": "s3",
             "scope": "tests", "reason": "bootstrap: create first RED test file for feature_900.alpha"},
            {"ts": "2026-01-07T00:00:00.000Z", "kind": "skip", "session": "s3",
             "scope": "src", "reason": "TDD bootstrap (GREEN side): impl for feature_900.alpha"},
        ]
        _seed_ledger(tmp_path, seed)
        out = _q_probe(json.dumps({"op": "audit"}), tmp_path=tmp_path)
        audit = out.get("skip_audit", [])
        # file order preserved (phase record excluded, skips in seed order)
        assert [e.get("ts") for e in audit] == [
            "2026-01-01T00:00:00.000Z", "2026-01-03T00:00:00.000Z",
            "2026-01-04T00:00:00.000Z", "2026-01-05T00:00:00.000Z",
            "2026-01-06T00:00:00.000Z", "2026-01-07T00:00:00.000Z",
        ]
        assert out.get("scope_tally") == {"tests": 4, "nav": 1, "src": 1}
        # global last-3 bootstrap reasons
        assert out.get("bootstrap_templates") == [
            "TDD_BOOTSTRAP: first tests/ write for feature_901.beta",
            "bootstrap: create first RED test file for feature_900.alpha",
            "TDD bootstrap (GREEN side): impl for feature_900.alpha",
        ]
        # per-feature filter: only reasons mentioning feature_900.alpha
        feat = _q_probe(json.dumps({"op": "audit", "feature": "feature_900.alpha"}),
                        session="ses_t1_1_feat", tmp_path=tmp_path)
        assert feat.get("bootstrap_templates") == [
            "TDD bootstrap: create RED file for feature_900.alpha",
            "bootstrap: create first RED test file for feature_900.alpha",
            "TDD bootstrap (GREEN side): impl for feature_900.alpha",
        ]
        assert feat.get("feature") == "feature_900.alpha"
