"""Overlay lane proofs (T3, harness_wrapper_split, feature_147).

Hermetic overlay contract for `prove --lane --overlay`: fixture trees (never the
real repo), injectable suite runner (never the real suite — minutes, not seconds).

RED shape: CLI/overlay API loaded lazily so missing impl FAILS (exit 1), never
breaks collection (exit 2). Follows `test_rename_away_meta.py` precedent.
"""

import importlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "omt"))

HARNESS_DIRS = [
    "scripts/omt",
    "scripts/session_inspect",
    ".opencode",
    ".meta",
]

SHARED_ROOTS = [
    "tests/__init__.py",
    "tests/conftest.py",
    "tests/constants.py",
    "tests/testing_utils.py",
]


def _cli():
    try:
        return importlib.import_module("split_proof")
    except ModuleNotFoundError as e:
        raise AssertionError(f"split_proof CLI missing (RED: implement overlay): {e}")


def _overlay_fn():
    cli = _cli()
    fn = getattr(cli, "build_overlay", None)
    assert fn is not None, "RED: split_proof.build_overlay missing (T3 overlay API)"
    return fn


def _fixture_root(base: Path) -> Path:
    """Minimal fake repo tree: both sides + shared roots + both lanes."""
    root = base / "fake_root"
    for rel in [
        "src/agentx/a.py",
        "scripts/omt/b.py",
        "scripts/session_inspect/c.py",
        ".opencode/d.ts",
        ".meta/e.json",
        "tests/agentx/t_agent.py",
        "tests/harness_meta/t_meta.py",
        *SHARED_ROOTS,
        "pyproject.toml",
    ]:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# fixture\n", encoding="utf-8")
    return root


def test_product_overlay_drops_harness_dirs(tmp_path):
    build_overlay = _overlay_fn()
    root = _fixture_root(tmp_path)
    dest = tmp_path / "out_product"
    out = Path(build_overlay(root, lane="product", dest=dest, overlay="tmpfs"))
    for rel in HARNESS_DIRS:
        assert not (out / rel).exists(), f"product overlay must drop {rel}"
    assert (out / "src" / "agentx" / "a.py").exists(), "product side must stay"
    assert (out / "tests" / "agentx" / "t_agent.py").exists(), "product lane must stay"
    for rel in SHARED_ROOTS:
        assert (out / rel).exists(), f"shared root must stay: {rel}"


def test_harness_overlay_drops_product(tmp_path):
    build_overlay = _overlay_fn()
    root = _fixture_root(tmp_path)
    dest = tmp_path / "out_harness"
    out = Path(build_overlay(root, lane="harness", dest=dest, overlay="tmpfs"))
    assert not (out / "src" / "agentx" / "a.py").exists(), "harness overlay must drop src/agentx"
    assert (out / "scripts" / "omt" / "b.py").exists(), "harness side must stay"
    assert (out / "tests" / "harness_meta" / "t_meta.py").exists(), "harness lane must stay"
    for rel in SHARED_ROOTS:
        assert (out / rel).exists(), f"shared root must stay: {rel}"


def test_suite_red_cuts_no_cert(tmp_path):
    cli = _cli()
    prove = getattr(cli, "prove_lane_overlay", None)
    assert prove is not None, "RED: split_proof.prove_lane_overlay missing"
    root = _fixture_root(tmp_path)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"python_exemptions": [], "ts_exemptions": []}))
    ledger = tmp_path / "ledger.jsonl"
    out = tmp_path / "certs"

    def red_runner(*a, **k):
        raise RuntimeError("suite RED (fixture)")

    try:
        prove("product", manifest, root, out, ledger, runner=red_runner)
    except SystemExit:
        pass
    else:
        raise AssertionError("RED: suite-red overlay must raise SystemExit (no cert)")
    assert not list(out.glob("*.cert.json")), "suite-red must cut no cert"


def test_suite_green_cuts_small_cert(tmp_path):
    cli = _cli()
    prove = getattr(cli, "prove_lane_overlay", None)
    assert prove is not None, "RED: split_proof.prove_lane_overlay missing"
    root = _fixture_root(tmp_path)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"python_exemptions": [], "ts_exemptions": []}))
    ledger = tmp_path / "ledger.jsonl"
    out = tmp_path / "certs"

    def green_runner(*a, **k):
        return 0

    dest = prove("product", manifest, root, out, ledger, runner=green_runner)
    raw = Path(dest).read_bytes()
    assert len(raw) <= 2048, f"cert exceeds 2 KiB: {len(raw)}"
    assert cli.check_cert_sha(json.loads(raw)), "cert_sha must verify"


def test_current_mode_keeps_v1_behavior(tmp_path):
    build_overlay = _overlay_fn()
    root = _fixture_root(tmp_path)
    out = Path(build_overlay(root, lane="product", dest=tmp_path / "noop", overlay="current"))
    assert out == root, "overlay=current must be the live tree (v1 compat, no copy)"


def test_tsc_clean_skip_open():
    """TS TA-strip CI check (T2 deferral): `tsc --noEmit` over the studio tree.

    Skip-open locally when the toolchain is absent (bun-canary precedent);
    strict in CI (the split.yml harness-lane job has the toolchain).
    """
    import shutil
    import subprocess

    import pytest

    studio = REPO / "tools" / "petri-net-studio"
    if not studio.is_dir():
        raise AssertionError("studio tree missing — cannot probe tsc")
    tsc = studio / "node_modules" / ".bin" / "tsc"
    if shutil.which("tsc") is None and not tsc.exists():
        pytest.skip("tsc toolchain absent locally (strict in CI)")
    cmd = [str(tsc) if tsc.exists() else "tsc", "--noEmit"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=180, cwd=str(studio))
    assert p.returncode == 0, f"tsc --noEmit must be clean:\n{p.stdout[-2000:]}\n{p.stderr[-2000:]}"
