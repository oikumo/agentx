"""Rename-away lane goldens (T2, harness_wrapper_split).

Overlay lane proofs v1 (zero moves): pins the four harness dirs renamed away
for the product lane + the shared build-root prerequisite, then proves both
lanes hermetically (tmp ledger, real ledger untouched).

Full `pytest tests/agentx` green with dirs renamed away is T3 acceptance
(blocked until T1/T3 lanes land) — this T2 pins the rename list + the import
firewall reason the rename is safe (zero runtime edges either way) + certs.

RED shape: CLI/manifest loaded lazily so missing impl FAILS (exit 1), never
breaks collection (exit 2).
"""

import importlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "omt"))

MANIFEST = REPO / "scripts" / "omt" / "split_proof_exemptions.json"
CLI = REPO / "scripts" / "omt" / "split_proof.py"

# Four harness dirs renamed away for the product lane (V7 §7 acceptance).
HARNESS_DIRS = [
    "scripts/omt",
    "scripts/session_inspect",
    ".opencode",
    ".meta",
]

# Shared build roots stay — both lanes import them in place (T1_SIGNOFF §1).
SHARED_ROOTS = [
    "tests/__init__.py",
    "tests/conftest.py",
    "tests/constants.py",
    "tests/testing_utils.py",
]

LOCKED_FIELDS = [
    "oracle",
    "lane",
    "file_rev",
    "live_rev",
    "ledger_sha",
    "firewall_verdict",
    "ta_ast_hash",
    "newcomer",
    "tokens_ms",
    "cert_sha",
]


def _cli():
    try:
        return importlib.import_module("split_proof")
    except ModuleNotFoundError as e:
        raise AssertionError(f"RED: split_proof module missing: {e}")


def test_rename_list_pinned_four_dirs():
    for rel in HARNESS_DIRS:
        p = REPO / rel
        assert p.is_dir(), f"rename-away dir missing: {rel}"
    assert len(HARNESS_DIRS) == 4


def test_shared_roots_pinned():
    for rel in SHARED_ROOTS:
        p = REPO / rel
        assert p.is_file(), f"shared build root missing: {rel}"


def test_product_without_harness_no_runtime_edges():
    # Executable reason the product-lane rename is safe: src/agentx holds
    # zero runtime imports to harness prefixes (AST, both forms).
    mod = _cli()
    edges: list[str] = []
    for py in sorted((REPO / "src" / "agentx").rglob("*.py")):
        edges.extend(mod.find_runtime_imports(py, direction="product_to_harness"))
    assert edges == [], f"product->harness edges block rename-away: {edges[:5]}"


def test_harness_without_product_no_runtime_edges():
    # Contract-pinned mirror: scripts/ holds zero runtime imports to product.
    mod = _cli()
    edges: list[str] = []
    base = REPO / "scripts"
    if base.is_dir():
        for py in sorted(base.rglob("*.py")):
            if ".venv" in py.parts:
                continue
            edges.extend(mod.find_runtime_imports(py, direction="harness_to_product"))
    assert edges == [], f"harness->product edges: {edges[:5]}"


def _run(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(REPO),
    )


def test_prove_both_hermetic_clean(tmp_path):
    led = tmp_path / "ledger.jsonl"
    real = REPO / ".meta" / ".omt" / "ledger.jsonl"
    before = real.read_bytes()
    p = _run("prove", "--lane", "both", "--out", str(tmp_path),
             "--ledger", str(led))
    assert p.returncode == 0, p.stderr
    assert "clean" in p.stdout.lower()
    certs = sorted(tmp_path.glob("*.cert.json"))
    assert len(certs) == 2
    for c in certs:
        raw = c.read_bytes()
        assert len(raw) <= 2048
        data = json.loads(raw)
        assert list(data.keys()) == LOCKED_FIELDS
        assert data["firewall_verdict"] == "clean"
        assert _cli().check_cert_sha(data)
    # Hermeticity under a PARALLEL suite: some other suite test appends the
    # real ledger (triage item 3, feature_138 test report) — byte-equality
    # across the window is racy. Honest pin: the real ledger only ever
    # GROWS (append-only), no growth row is a split_proof.* kind (only
    # prove/attest write those, and ours went to --ledger tmp), and the
    # tmp ledger carries exactly our two cert rows.
    after = real.read_bytes()
    assert after.startswith(before), "real ledger mutated outside append"
    growth = [ln for ln in after[len(before):].splitlines() if ln.strip()]
    for ln in growth:
        assert not json.loads(ln).get("kind", "").startswith("split_proof."), (
            "prove wrote split_proof rows to the REAL ledger"
        )
    rows = [json.loads(l) for l in led.read_text().splitlines()]
    assert [r["kind"] for r in rows] == ["split_proof.cert", "split_proof.cert"]
    assert [r["lane"] for r in rows] == ["product", "harness"]
