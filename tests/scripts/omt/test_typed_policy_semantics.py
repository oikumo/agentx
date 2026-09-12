"""T4-1 typed policy semantics (feature_072.typed_policy_semantics).

Golden: ONE evaluator (policy_decision.evaluatePolicy) returns identical
decisions for preflight / enforcement / explain on the same snapshot;
g.net activation (solo skip, C1) + break-glass exception (expiring
scope=all, audited) are explicit typed data; durable progress survives temp
expiry and is feature-scoped (A cannot move B).
"""

import json
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
POLICY_MOD = REPO_ROOT / ".opencode" / "lib" / "enforcer" / "policy_decision.ts"

BUN = shutil.which("bun")

_PROBE_TEMPLATE = """
import { evaluatePolicy, explainDecision, hasDurableProgress } from "%MOD%"
const snap = %SNAP%
const d = evaluatePolicy(snap)
// simulate the three call sites sharing ONE evaluator
const preflight = evaluatePolicy(snap)
const enforcement = evaluatePolicy(snap)
const explained = explainDecision(snap.gate, d)
console.log(JSON.stringify({ d, preflight, enforcement, explained,
  durable: hasDurableProgress(snap.records, snap.feature, snap.session, snap.nowMs) }))
"""


def _probe(snap: dict, tmp_path: Path) -> dict:
    assert BUN is not None, "bun runtime required"
    probe = tmp_path / "probe_t41.ts"
    probe.write_text(
        _PROBE_TEMPLATE.replace("%MOD%", str(POLICY_MOD)).replace(
            "%SNAP%", json.dumps(snap)),
        encoding="utf-8",
    )
    out = subprocess.run([BUN, str(probe)], capture_output=True, text=True,
                         timeout=60, cwd=str(REPO_ROOT))
    assert out.returncode == 0, f"bun probe failed:\n{out.stderr}\n---"
    return json.loads(out.stdout.strip().splitlines()[-1])


def _ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TestTypedPolicySemantics:
    """T4-1: one evaluator, explicit activation/exception, durable vs temp."""

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_solo_activation_skips(self, tmp_path):
        now = _now()
        snap = {"gate": "g.net", "session": "ses_a",
                "nowMs": int(now.timestamp() * 1000), "records": [],
                "netMarking": {"work_active": 1, "activeHolders": ["f1_active"]}}
        r = _probe(snap, tmp_path)
        assert r["d"]["allowed"] is True
        assert r["d"]["via"] == "activation_solo_skip"
        # parity: preflight == enforcement == explain input
        assert r["preflight"]["via"] == r["enforcement"]["via"] == "activation_solo_skip"
        assert "solo" in r["explained"]

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_concurrent_without_grant_denies(self, tmp_path):
        now = _now()
        snap = {"gate": "g.net", "session": "ses_a",
                "nowMs": int(now.timestamp() * 1000), "records": [],
                "netMarking": {"work_active": 2,
                               "activeHolders": ["f1_active", "f2_active"]}}
        r = _probe(snap, tmp_path)
        assert r["d"]["allowed"] is False
        assert r["d"]["via"] == "deny_concurrent_no_grant"
        assert r["preflight"] == r["enforcement"]
        assert "fire" in r["explained"] or "concurrent" in r["explained"]

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_concurrent_break_glass_allows(self, tmp_path):
        now = _now()
        recs = [{"kind": "skip", "scope": "all", "reason": "break glass demo",
                 "session": "ses_a", "ts": _ts(now - timedelta(hours=1))}]
        snap = {"gate": "g.net", "session": "ses_a",
                "nowMs": int(now.timestamp() * 1000), "records": recs,
                "netMarking": {"work_active": 2,
                               "activeHolders": ["f1_active", "f2_active"]}}
        r = _probe(snap, tmp_path)
        assert r["d"]["allowed"] is True
        assert r["d"]["via"] == "exception_break_glass"
        assert r["preflight"]["via"] == r["enforcement"]["via"]
        assert "break-glass" in r["explained"]

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_expired_break_glass_denies_but_progress_survives(self, tmp_path):
        now = _now()
        recs = [
            {"kind": "skip", "scope": "all", "reason": "old glass",
             "session": "ses_a", "ts": _ts(now - timedelta(hours=9))},
            {"kind": "phase", "phase": "Programming", "feature": "feature_A",
             "task_type": "minor_feature", "scope": "s",
             "session": "ses_a", "ts": _ts(now - timedelta(hours=1))},
        ]
        snap = {"gate": "g.net", "session": "ses_a", "feature": "feature_A",
                "nowMs": int(now.timestamp() * 1000), "records": recs,
                "netMarking": {"work_active": 2,
                               "activeHolders": ["f1_active", "f2_active"]}}
        r = _probe(snap, tmp_path)
        # expiry removes authority ...
        assert r["d"]["allowed"] is False
        assert r["d"]["via"] == "deny_concurrent_no_grant"
        # ... without losing task progress (durable, feature-scoped)
        assert r["durable"] is True
        # feature isolation: B has no progress from A's records
        snap_b = dict(snap, feature="feature_B")
        rb = _probe(snap_b, tmp_path)
        assert rb["durable"] is False
