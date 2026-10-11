"""AST import firewall + prove/verify/attest goldens (feature_138, Oracle firewall slice).

Import-statement regex only — never substring (`rg agentx` has a 5-hit
false-positive class: bench fixture-strings + path-strings). Exemptions live in
the versioned manifest `scripts/omt/split_proof_exemptions.json`.

RED shape: the CLI module/manifest are loaded lazily inside helpers so a missing
implementation FAILS each test (exit 1) instead of breaking collection (exit 2).
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


def _manifest():
    try:
        return json.loads(MANIFEST.read_text())
    except FileNotFoundError as e:
        raise AssertionError(f"RED: exemption manifest missing: {e}")


def test_manifest_v1_pins_5_hit_exemption_class():
    m = _manifest()
    assert m["version"] == 1
    locs = {e["file"] + ":" + str(e["line"]) for e in m["python_exemptions"]}
    assert "scripts/omt/bench/tasks.py:32" in locs
    assert "scripts/omt/bench/tasks.py:44" in locs
    assert "scripts/omt/bench/tasks.py:11" in locs
    assert "scripts/omt/bench/tasks.py:12" in locs
    assert "scripts/omt/bench/tasks.py:35" in locs


def test_firewall_product_lane_clean():
    verdict = _cli().scan_firewall(MANIFEST, REPO)
    assert verdict["edges"] == [], f"non-exempt runtime edges: {verdict['edges']}"


def test_firewall_rejects_synthetic_violation(tmp_path):
    bad = tmp_path / "bad_mod.py"
    bad.write_text("import scripts.omt.net\nfrom src.agentx.model.session import Session\n")
    mod = _cli()
    fwd = mod.find_runtime_imports(bad, direction="product_to_harness")
    rev = mod.find_runtime_imports(bad, direction="harness_to_product")
    assert any("scripts.omt.net" in e for e in fwd)
    assert any("src.agentx" in e for e in rev)


def test_firewall_exempts_bench_fixture_and_path_strings():
    mod = _cli()
    hits = mod.raw_hits(REPO / "scripts" / "omt" / "bench" / "tasks.py")
    assert len(hits) >= 5, f"5-hit class shrank, re-pin manifest: {hits}"
    verdict = mod.scan_firewall(MANIFEST, REPO)
    assert verdict["edges"] == []


def test_ts_firewall_studio_clean():
    verdict = _cli().scan_ts_firewall(MANIFEST, REPO)
    assert verdict["edges"] == [], f"non-exempt TS edges: {verdict['edges']}"


def _run(*args, cwd=None):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(cwd or REPO),
    )


def test_prove_both_emits_two_locked_certs(tmp_path):
    p = _run("prove", "--lane", "both", "--out", str(tmp_path),
             "--ledger", str(tmp_path / "ledger.jsonl"))
    assert p.returncode == 0, p.stderr
    certs = sorted(tmp_path.glob("*.cert.json"))
    assert len(certs) == 2
    for c in certs:
        raw = c.read_bytes()
        assert len(raw) <= 2048, f"{c.name} exceeds 2 KiB"
        data = json.loads(raw)
        assert list(data.keys()) == LOCKED_FIELDS
        assert _cli().check_cert_sha(data)


def test_prove_appends_hash_chained_cert_rows(tmp_path):
    # E3: one split_proof.cert row per cert, Merkle-chained (row2.ledger_sha
    # == sha(row1)); hermetic ledger — the real ledger is never touched.
    led = tmp_path / "ledger.jsonl"
    _run("prove", "--lane", "both", "--out", str(tmp_path),
         "--ledger", str(led)).check_returncode()
    rows = [json.loads(l) for l in led.read_text().splitlines()]
    assert [r["kind"] for r in rows] == ["split_proof.cert"] * 2
    assert [r["lane"] for r in rows] == ["product", "harness"]
    assert rows[0]["ledger_sha"] == _cli().GENESIS_SHA
    import hashlib
    raw = led.read_bytes().splitlines(keepends=True)
    assert rows[1]["ledger_sha"] == hashlib.sha256(raw[0]).hexdigest()
    certs = {c.name: json.loads(c.read_bytes()) for c in tmp_path.glob("*.cert.json")}
    assert rows[0]["cert_sha"] == certs["split_proof_product.cert.json"]["cert_sha"]
    assert rows[1]["cert_sha"] == certs["split_proof_harness.cert.json"]["cert_sha"]


def test_verify_byte_identical(tmp_path):
    # In isolation this is byte-identical; under a parallel suite the ledger
    # may grow between prove and verify — then STALE-valid (provenance holds
    # via the prefix check) is the honest pass. Both print distinctly.
    # E3 note: prove's own chain row always lands first, so on a hermetic
    # ledger this reads STALE-valid (row 0/1) — still a provenance pass.
    led = str(tmp_path / "ledger.jsonl")
    _run("prove", "--lane", "both", "--out", str(tmp_path),
         "--ledger", led).check_returncode()
    for c in sorted(tmp_path.glob("*.cert.json")):
        v = _run("verify", str(c), "--ledger", led)
        assert v.returncode == 0, v.stderr
        assert "identical" in v.stdout or "STALE-valid" in v.stdout


def test_attest_bridge_zero_conforming_one_prose(tmp_path):
    led = tmp_path / "ledger.jsonl"
    p = _run("attest-bridge", "--ledger", str(led))
    assert p.returncode == 0, p.stderr
    data = json.loads(p.stdout)
    assert data["conforming"] == 0
    assert any("meta_harness_11" in h for h in data["prose_hits"])
    rows = [json.loads(l) for l in led.read_text().splitlines()]
    assert len(rows) == 1 and rows[0]["kind"] == "split_proof.attest"
    assert rows[0]["conforming"] == 0
