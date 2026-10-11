"""Feature 147 gate-alignment unit tests (T3 overlay lane proofs).

Phase-gate Programming->Testing requires tests/<lane>/<feature>/test_*.py
(lane-aware checkPhaseExitArtifacts). The hermetic oracle goldens live in
tests/harness_meta/split_proof_meta/test_overlay_meta.py (shared oracle dir,
per design_001 E4) — this dir holds the feature's OWN unit tests (same
contract, fixture trees, injected runner never the real suite) so the exit
gate resolves without moving the oracle.

Covers scripts/omt/split_proof.py overlay surface: OVERLAY_* pins +
build_overlay tmpfs/current behavior.
"""

import importlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "omt"))

SHARED_ROOTS = [
    "tests/__init__.py",
    "tests/conftest.py",
    "tests/constants.py",
    "tests/testing_utils.py",
]


def _cli():
    return importlib.import_module("split_proof")


def test_overlay_constants_pin_harness_dirs_and_roots():
    cli = _cli()
    assert tuple(cli.OVERLAY_PRODUCT_DROP) == (
        "scripts/omt",
        "scripts/session_inspect",
        ".opencode",
        ".meta",
    )
    assert tuple(cli.OVERLAY_HARNESS_DROP) == ("src/agentx",)
    assert tuple(cli.OVERLAY_SHARED_ROOTS) == tuple(SHARED_ROOTS)
    assert cli.OVERLAY_LANE_SUITE["product"] == ("tests/agentx",)
    assert cli.OVERLAY_LANE_SUITE["harness"] == ("tests/harness_meta",)


def _fixture_root(base: Path) -> Path:
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


def test_overlay_product_tmpfs_drops_harness_keeps_shared(tmp_path):
    cli = _cli()
    root = _fixture_root(tmp_path)
    out = Path(cli.build_overlay(root, lane="product", dest=tmp_path / "out_p", overlay="tmpfs"))
    for rel in cli.OVERLAY_PRODUCT_DROP:
        assert not (out / rel).exists(), f"product overlay must drop {rel}"
    assert (out / "src" / "agentx" / "a.py").exists()
    assert (out / "tests" / "agentx" / "t_agent.py").exists()
    for rel in SHARED_ROOTS:
        assert (out / rel).exists(), f"shared root must stay: {rel}"


def test_overlay_current_mode_keeps_live_tree(tmp_path):
    cli = _cli()
    root = _fixture_root(tmp_path)
    out = Path(cli.build_overlay(root, lane="product", dest=tmp_path / "noop", overlay="current"))
    assert out == root
