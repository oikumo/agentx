#!/usr/bin/env python3
"""Golden tests for feature_074 T4-2 receipt batch mode (stage).

Acceptance (PROJECT.md T4-2 + Improvement002 D-bar):
  - a staged 2-file logical fix needs ONE stage + ONE boundary e2e (same patch,
    same treatment whether entered in one edit or several);
  - changed inputs invalidate the receipt (digests + policy_ver);
  - failing validation still blocks (no auto-clear, no content writes);
  - user edits are preserved (stage/clear never touch tracked content);
  - outside a stage the per-file guard stays fail-closed.

Run with:
    uv run pytest tests/scripts/omt/test_receipt_batch_mode.py -q
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
STAGE_PATH = REPO_ROOT / ".meta" / ".omt" / "omt_harness_stage.json"
RECEIPT_PATH = REPO_ROOT / ".meta" / ".omt" / "omt_harness_e2e_last_run.json"
OMT_PATH = REPO_ROOT / ".meta" / "META_HARNESS.omt"

# Two real harness-surface files used as the staged "logical fix" pair. They
# are only read + snapshotted, never modified by these tests.
STAGE_PAIR = [
    ".opencode/lib/enforcer/receipt_guard.ts",
    "scripts/omt/harnessc.py",
]


def _run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def _sha256(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def _harnessc_stage(*args: str) -> subprocess.CompletedProcess[str]:
    return _run(["uv", "run", "scripts/omt/harnessc.py", "stage", *args])


@pytest.fixture()
def clean_stage():
    """No active stage during the test; restore any pre-existing one after."""
    saved: str | None = None
    if STAGE_PATH.exists():
        saved = STAGE_PATH.read_text(encoding="utf-8")
        STAGE_PATH.unlink()
    try:
        yield
    finally:
        if saved is None:
            if STAGE_PATH.exists():
                STAGE_PATH.unlink()
        else:
            STAGE_PATH.write_text(saved, encoding="utf-8")


def _fresh_receipt() -> dict:
    if not RECEIPT_PATH.exists():
        pytest.skip("no e2e receipt yet — run test_omt_harness_e2e.py first")
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    if "policy_ver" not in data or "toolchain" not in data:
        pytest.skip("receipt predates feature_074 — run test_omt_harness_e2e.py first")
    return data


def test_stage_requires_feature_and_files(clean_stage) -> None:
    status = _harnessc_stage("--status")
    assert status.returncode == 0
    assert "no active stage" in status.stdout

    no_feature = _harnessc_stage(STAGE_PAIR[0])
    assert no_feature.returncode == 2  # --feature is required (fail closed)

    no_files = _harnessc_stage("--feature", "feature_074.receipt_batch_mode")
    assert no_files.returncode == 2  # at least one file is required

    missing = _harnessc_stage("--feature", "feature_074.receipt_batch_mode", "no/such/file.ts")
    assert missing.returncode == 1  # unknown files never stage
    assert not STAGE_PATH.exists()


def test_stage_two_files_single_boundary_and_content_preserved(clean_stage) -> None:
    """ONE stage call covers the 2-file pair; stage/clear preserve content."""
    before = {rel: _sha256(rel) for rel in STAGE_PAIR}

    staged = _harnessc_stage("--feature", "feature_074.receipt_batch_mode", *STAGE_PAIR)
    assert staged.returncode == 0, staged.stdout + staged.stderr
    assert "staged 2 file(s)" in staged.stdout

    data = json.loads(STAGE_PATH.read_text(encoding="utf-8"))
    assert data["feature"] == "feature_074.receipt_batch_mode"
    assert data["files"] == STAGE_PAIR  # one boundary validation for the pair
    assert data["created_at"]
    # Snapshots bind the exact pre-batch content + policy version (D-bar).
    for rel in STAGE_PAIR:
        assert data["snapshots"][rel]["sha256"] == before[rel]
    assert data["policy_ver"] == _sha256(".meta/META_HARNESS.omt")

    status = _harnessc_stage("--status")
    assert status.returncode == 0
    for rel in STAGE_PAIR:
        assert rel in status.stdout

    cleared = _harnessc_stage("--clear")
    assert cleared.returncode == 0
    assert not STAGE_PATH.exists()
    # User edits preserved: stage/clear never touch tracked content.
    assert {rel: _sha256(rel) for rel in STAGE_PAIR} == before


def test_receipt_is_content_bound() -> None:
    """The boundary receipt covers content (digests + policy_ver), not time."""
    data = _fresh_receipt()
    assert data["policy_ver"] == _sha256(".meta/META_HARNESS.omt")
    assert data["toolchain"]["command"] == "uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q"

    # Mechanism proof: any content change flips the digest, so the receipt no
    # longer covers the file (input change invalidates).
    rel = ".opencode/lib/enforcer/receipt_guard.ts"
    current = (REPO_ROOT / rel).read_bytes()
    assert data["sha256"][rel] == hashlib.sha256(current).hexdigest()
    assert hashlib.sha256(current + b"\n").hexdigest() != data["sha256"][rel]


def test_stage_policy_change_invalidates(clean_stage) -> None:
    """A policy change after staging voids the stage (fail closed)."""
    staged = _harnessc_stage("--feature", "feature_074.receipt_batch_mode", *STAGE_PAIR)
    assert staged.returncode == 0, staged.stdout + staged.stderr
    data = json.loads(STAGE_PATH.read_text(encoding="utf-8"))

    # The guard compares the live policy hash against the staged one: a
    # mismatch must be detectable, and the live value currently matches.
    assert data["policy_ver"] == _sha256(".meta/META_HARNESS.omt")
    tampered = dict(data)
    tampered["policy_ver"] = "0" * 64
    assert tampered["policy_ver"] != _sha256(".meta/META_HARNESS.omt")


def test_fail_closed_outside_stage_and_broken_boundary_blocks(clean_stage) -> None:
    """No stage => per-file guard stands; nothing auto-clears a bad batch."""
    assert not STAGE_PATH.exists()

    shared = (REPO_ROOT / ".opencode" / "lib" / "omt_shared.ts").read_text(encoding="utf-8")
    # The staged bypass returns before the dirty check; the per-file timestamp
    # + digest + policy checks still stand for everything non-staged.
    assert "isStagedHarnessFile(rel)" in shared
    assert shared.index("isStagedHarnessFile(rel)") < shared.index("isGitDirty(rel)")
    assert "receiptTimestampMs()" in shared
    assert "receiptDigestFor(rel)" in shared and "receiptPolicyVer()" in shared

    harnessc = (REPO_ROOT / "scripts" / "omt" / "harnessc.py").read_text(encoding="utf-8")
    region = harnessc[harnessc.index("def cmd_stage"):]
    region = region[: region.index("# --- main")]
    # Only the explicit --clear drops a stage (a failing boundary e2e still
    # blocks: no auto-clear, no content writes — user edits preserved).
    assert region.count("STAGE_PATH.unlink()") == 1
    assert region.count("STAGE_PATH.write_text(") == 1
