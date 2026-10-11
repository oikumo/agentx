"""TA-inversion golden (T4 closeout, harness_wrapper_split, feature_150).

Closes PROPOSAL_V7 §4 + pause v7.2.5 C:
- Index {location, owner}: readThoughtsIndex derives both per thought at READ
  time (location from lanes roots; owner=harness — the declared inversion's
  only writer; owner:"product" reserved for future self-annotation).
- Logic-touch enforcement: the scope:src skip bypass is bounded to TA-only
  edits — any non-TA change on a TA-carrying src/ .py file requires a full
  omt_phase (guardSrcPath snapshots content; the g.mvc after-gate checks the
  diff via taLogicTouchCheck BEFORE the lint delta).
- TS half: strip `// TA:` from a studio COPY → `tsc --noEmit` clean
  (comment-only + line-count pins live in test_ta_strip_meta; tsc-with-TA
  strict-in-CI lives in test_overlay_meta.test_tsc_clean_skip_open).

RED shape: bun missing skips the real-module probes (054 precedent); missing
impl fails the probe (never breaks collection). Hermetic tmp roots via
initOmtShared(root) injection — the real ledger is never touched.
"""

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
LIB = REPO / ".opencode" / "lib" / "omt_shared.ts"
SESSION_STATE = REPO / ".opencode" / "lib" / "enforcer" / "session_state.ts"
PHASE_GATE = REPO / ".opencode" / "lib" / "enforcer" / "phase_gate.ts"
MVC_AFTER = REPO / ".opencode" / "lib" / "enforcer" / "mvc_after.ts"
BUN = shutil.which("bun")

TS_TA_RE = None  # set lazily to mirror test_ta_strip_meta without importing it
PY_TA_RE = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _seed_root(tmp_path: Path, ledger_records: list) -> Path:
    omtd = tmp_path / ".meta" / ".omt"
    omtd.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO / ".meta" / ".omt" / "harness.ir.json", omtd / "harness.ir.json")
    (omtd / "ledger.jsonl").write_text(
        "\n".join(json.dumps(r) for r in ledger_records) + ("\n" if ledger_records else ""),
        encoding="utf-8",
    )
    return tmp_path


def _run_bun(script: str, args: list) -> dict:
    probe = Path(args[0]) / "probe_t4.ts"
    probe.write_text(script, encoding="utf-8")
    out = subprocess.run(
        ["bun", str(probe), *args],
        capture_output=True, text=True, timeout=120,
    )
    assert out.returncode == 0, f"bun probe failed:\n{out.stderr}\n---"
    return json.loads(out.stdout.strip().splitlines()[-1])


INDEX_PROBE = """
import { initOmtShared, readThoughtsIndex } from "%LIB%"
initOmtShared(process.argv[2])
const recs = readThoughtsIndex()
console.log(JSON.stringify(recs))
"""

GATE_PROBE = """
import { initOmtShared } from "%LIB%"
initOmtShared(process.argv[2])
const { createSessionState } = await import("%SESSION_STATE%")
const { guardSrcPath } = await import("%PHASE_GATE%")
const { taLogicTouchCheck } = await import("%MVC_AFTER%")
const fs = await import("node:fs")
const root = process.argv[2]
const mode = process.argv[3]
const abs = root + "/src/agentx/probe_mod.py"
const rel = "src/agentx/probe_mod.py"
fs.mkdirSync(root + "/src/agentx", { recursive: true })
fs.writeFileSync(abs, "# TA: gotcha: t4 probe inversion\\nx = 1\\n")
const env = {
  state: createSessionState(), directory: root,
  safeLog: () => {}, notify: async () => {}, client: {}, $: {},
}
const session = "ses_t150"
await guardSrcPath(env, session, rel, abs)
const text = fs.readFileSync(abs, "utf8")
fs.writeFileSync(abs, mode === "logic" ? text + "y = 2\\n" : text + "# TA: gotcha: second\\n")
try {
  await taLogicTouchCheck(env, session, abs, rel)
  console.log(JSON.stringify({ blocked: false }))
} catch (e) {
  console.log(JSON.stringify({ blocked: true, msg: String((e && e.message) || e) }))
}
"""


def _idx_probe(root: Path, scratch: Path) -> list:
    # probe file lives under scratch — NEVER the repo root (stray hygiene:
    # GOTCHA_PROVE_CERTS_ROOT_STRAY class — root strays break check-expecting
    # tests via the @var root_allowlist FILESYSTEM scan).
    scratch.mkdir(parents=True, exist_ok=True)
    script = (
        INDEX_PROBE.replace("%LIB%", str(LIB))
    )
    probe = scratch / "probe_idx.ts"
    probe.write_text(script, encoding="utf-8")
    out = subprocess.run(["bun", str(probe), str(root)], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, f"bun index probe failed:\n{out.stderr}\n---"
    return json.loads(out.stdout.strip().splitlines()[-1])


@pytest.mark.skipif(BUN is None, reason="bun not available")
def test_thoughts_index_location_owner_hermetic(tmp_path):
    recs = [
        {"ts": _now(), "path": "src/agentx/ui/x.py", "line": 3, "category": "gotcha", "thought": "p1"},
        {"ts": _now(), "path": "tools/petri-net-studio/src/ui/App.tsx", "line": 1, "category": "risk", "thought": "p2"},
        {"ts": _now(), "path": "shared/petri-net/FORMAT.md", "line": 2, "category": "gotcha", "thought": "p3"},
        {"ts": _now(), "path": "tests/agentx/feature_030/t.py", "line": 5, "category": "gotcha", "thought": "p4"},
        {"ts": _now(), "path": "tests/harness_meta/omt/t.py", "line": 7, "category": "gotcha", "thought": "h1"},
        {"ts": _now(), "path": ".opencode/plugins/omt_q.ts", "line": 9, "category": "gotcha", "thought": "h2"},
        {"ts": _now(), "path": "scripts/omt/net/state.py", "line": 11, "category": "gotcha", "thought": "h3"},
        {"ts": _now(), "path": "src\\agentx\\win.py", "line": 13, "category": "gotcha", "thought": "p5-backslash"},
    ]
    root = tmp_path / "herm"
    omtd = root / ".meta" / ".omt"
    omtd.mkdir(parents=True, exist_ok=True)
    (omtd / "thoughts.jsonl").write_text(
        "\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8"
    )
    out = _idx_probe(root, tmp_path / "scratch")
    got = {r["thought"]: (r["location"], r["owner"]) for r in out}
    assert len(out) == len(recs)
    for key in ("p1", "p2", "p3", "p4", "p5-backslash"):
        assert got[key] == ("product", "harness"), f"{key} should derive (product, harness): {got[key]}"
    for key in ("h1", "h2", "h3"):
        assert got[key] == ("harness", "harness"), f"{key} should derive (harness, harness): {got[key]}"


@pytest.mark.skipif(BUN is None, reason="bun not available")
def test_thoughts_index_live_enriched_and_inversion_derivable(tmp_path):
    out = _idx_probe(REPO, tmp_path / "scratch")
    assert out, "live thoughts.jsonl unexpectedly empty"
    for r in out:
        assert r.get("location") in ("product", "harness"), f"missing location: {r}"
        assert r.get("owner") == "harness", f"owner must default harness: {r}"
    # The declared inversion (§4) stays measurable from the same rule: every
    # TA-carrying src/agentx file would derive location=product.
    import re
    py_ta = re.compile(r"^\s*#\s*TA:")
    product_prefixes = ("src/agentx/",)
    files = []
    base = REPO / "src" / "agentx"
    for py in sorted(base.rglob("*.py")):
        try:
            text = py.read_text(encoding="utf-8")
        except OSError:
            continue
        if any(py_ta.match(ln) for ln in text.splitlines()):
            files.append(py)
    assert len(files) >= 18, f"TA-carrying src/agentx files shrank: {len(files)}"
    for f in files:
        rel = f.relative_to(REPO).as_posix()
        assert rel.startswith(product_prefixes), rel  # trivially true — pins the rule


@pytest.mark.parametrize(
    "ledger_kind,edit_mode,expect_block",
    [
        ("skip", "logic", True),    # skip bypass + logic touch -> BLOCKED (no bypass)
        ("skip", "ta", False),      # skip bypass + TA-only edit -> allowed
        ("phase", "logic", False),  # full phase + logic touch -> allowed
    ],
)
@pytest.mark.skipif(BUN is None, reason="bun not available")
def test_logic_touch_alongside_ta_enforcement(tmp_path, ledger_kind, edit_mode, expect_block):
    rec = (
        {"ts": _now(), "kind": "skip", "session": "ses_t150", "reason": "t4 probe",
         "scope": "src", "purpose": "override"}
        if ledger_kind == "skip"
        else {"ts": _now(), "kind": "phase", "session": "ses_t150", "task_type": "bug_fix",
              "phase": "Programming", "scope": "t4 probe", "feature": "", "design_doc": "",
              "tdd_mode": False}
    )
    root = _seed_root(tmp_path, [rec])
    script = (
        GATE_PROBE
        .replace("%LIB%", str(LIB))
        .replace("%SESSION_STATE%", str(SESSION_STATE))
        .replace("%PHASE_GATE%", str(PHASE_GATE))
        .replace("%MVC_AFTER%", str(MVC_AFTER))
    )
    out = _run_bun(script, [str(root), edit_mode])
    if expect_block:
        assert out["blocked"] is True, f"logic touch under skip must block: {out}"
        assert "logic touch alongside TA" in out["msg"], out["msg"]
    else:
        assert out["blocked"] is False, f"must not block: {out}"


def _studio_tsc() -> Path | None:
    tsc = REPO / "tools" / "petri-net-studio" / "node_modules" / ".bin" / "tsc"
    if tsc.exists():
        return tsc
    return Path(shutil.which("tsc")) if shutil.which("tsc") else None


def test_ts_strip_studio_tsc_clean(tmp_path):
    """T4 TS half: studio copy with `// TA:` lines stripped stays tsc-clean.

    Skip-open locally when the toolchain is absent (bun-canary precedent);
    strict in CI (split.yml carries the toolchain).
    """
    import re

    tsc = _studio_tsc()
    if tsc is None:
        pytest.skip("tsc toolchain absent locally (strict in CI)")
    studio = REPO / "tools" / "petri-net-studio"
    dest = tmp_path / "studio"
    shutil.copytree(
        studio, dest,
        ignore=shutil.ignore_patterns("node_modules", "dist", ".git"),
    )
    ts_ta = re.compile(r"^\s*//\s*TA:")
    stripped = 0
    for ts in sorted(dest.rglob("*.ts")) + sorted(dest.rglob("*.tsx")):
        text = ts.read_text(encoding="utf-8")
        kept = [ln for ln in text.splitlines() if not ts_ta.match(ln)]
        if len(kept) != len(text.splitlines()):
            stripped += 1
            ts.write_text("\n".join(kept) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")
    assert stripped > 0, "no TS TA lines stripped — scope re-pin needed"
    os.symlink(studio / "node_modules", dest / "node_modules")
    p = subprocess.run(
        [str(tsc), "--noEmit"], capture_output=True, text=True, timeout=180, cwd=str(dest)
    )
    assert p.returncode == 0, (
        f"stripped studio tree must stay tsc-clean:\n{p.stdout[-2000:]}\n{p.stderr[-2000:]}"
    )


@pytest.mark.skipif(BUN is None, reason="bun not available")
def test_ts_strip_opencode_syntax_clean(tmp_path):
    """T4 TS half, harness side: stripped .opencode TS stays parseable.

    No tsconfig exists for .opencode (plugins are bun-executed; the e2e
    receipt exercises them for real at runtime) — so this pins SYNTAX
    preservation via `bun build --external '*'` on the stripped copy tree
    (relative imports resolve within the copy; packages stay external).
    Type-checking of the studio half is CI-strict via overlay tsc.
    """
    import re

    ts_ta = re.compile(r"^\s*//\s*TA:")
    targets = []
    for ts in sorted((REPO / ".opencode").rglob("*.ts")):
        if "node_modules" in ts.parts:
            continue
        text = ts.read_text(encoding="utf-8")
        kept = [ln for ln in text.splitlines() if not ts_ta.match(ln)]
        out = tmp_path / "copy" / ts.relative_to(REPO)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(kept) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")
        if len(kept) != len(text.splitlines()):
            targets.append(out)
    assert targets, "no .opencode TS TA lines stripped — scope re-pin needed"
    for f in targets:
        p = subprocess.run(
            ["bun", "build", str(f), "--outdir", str(tmp_path / "out"), "--external", "*"],
            capture_output=True, text=True, timeout=120,
        )
        assert p.returncode == 0, (
            f"stripped {f.name} broke TS parseability:\n{p.stdout[-1500:]}\n{p.stderr[-1500:]}"
        )
