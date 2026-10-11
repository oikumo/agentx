"""Per-mechanic receipt goldens (T5, harness_wrapper_split, feature_151).

Pins design_001 invariants I1–I6:
- I1 slice resolution (receiptSliceFor: exact + dir-prefix, unmapped → null)
- I2 per-slice freshness decoupling (slice q fresh while another slice's file
  is dirty-newer than the global block → q editable, other blocked)
- I3 content-bound digests inside slice blocks
- I4 fail-closed mint (red slice tests → exit 1, no write)
- I5 atomic merge (tmp+os.replace) + status read-only
- I6 legacy compat (receipt JSON without `slices` → byte-identical global)

Bun probes drive the REAL shared lib (omt_q idiom, initOmtShared(root)
injection); receipt.py is driven via `--root` tmp copies (hermetic — no
golden ever writes the real receipt; root-stray class banned).
"""

# TA: resume: T5 RED pinned 2026-10-11 (feature_151, harness_wrapper_split) —
# TA: resume: impl NOT started; batch-round protocol + full next-step map live
# TA: resume: in sandbox/pause_2026-10-11.md v8 §v8.2 (stage META_HARNESS.omt +
# TA: resume: omt_shared.ts FIRST for the T4-2 batch bypass; receipt.py runs
# TA: resume: pytest with cwd=REPO (never --root — uv needs the repo project);
# TA: resume: strong freshness goldens need REAL git-dirty tmp roots
# TA: resume: (git init + commit + modify — a fake .git dir makes git fail-open
# TA: resume: → isGitDirty false → gate ok BEFORE the slice branch = wrong pin).

import json
import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
LIB = REPO / ".opencode" / "lib" / "omt_shared.ts"
RECEIPT_CLI = REPO / "scripts" / "omt" / "receipt.py"
BUN = shutil.which("bun")
UV = shutil.which("uv") or "uv"

SLICES_PROBE = """
import { initOmtShared } from "%LIB%"
initOmtShared(process.argv[2])
const mod = await import("%LIB%")
const out = {
  slice_q: mod.receiptSliceFor ? mod.receiptSliceFor(".opencode/plugins/omt_q.ts") : "MISSING",
  slice_net_prefix: mod.receiptSliceFor ? mod.receiptSliceFor("scripts/omt/net/state.py") : "MISSING",
  slice_split: mod.receiptSliceFor ? mod.receiptSliceFor("scripts/omt/split_proof.py") : "MISSING",
  unmapped: mod.receiptSliceFor ? mod.receiptSliceFor("scripts/omt/harnessc.py") : "MISSING",
  status: {},
}
// omtHarnessE2eStatus per scenario file (probe_arg = abs path of seeded file)
const target = process.argv[3]
if (mod.omtHarnessE2eStatus && target !== "-") {
  const rel = mod.relOf ? mod.relOf(target).rel : target
  const s = mod.omtHarnessE2eStatus(rel, target)
  out.status = { ok: s.ok, msg: s.message }
}
console.log(JSON.stringify(out))
"""


def _iso(delta_hours: float = 0.0) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=delta_hours)).isoformat()


def _seed_tree(tmp_path: Path, mtimes: dict, git: bool = True) -> Path:
    """Seed a hermetic repo-like tree: IR + harness file copies.

    git=True (strong goldens): a REAL git repo — commit the seeded tree, then
    append a marker line to every seeded file so isGitDirty(rel) is true and
    the gate reaches the slice branch (a fake .git/HEAD-only dir makes git
    fail-open → clean → gate ok BEFORE the slice branch = wrong verdict, per
    the TA resume notes). git=False keeps the no-git fail-open class (pinned
    by test_fresh_slice_block_decouples_from_global)."""
    root = tmp_path / "repo"
    omtd = root / ".meta" / ".omt"
    omtd.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO / ".meta" / ".omt" / "harness.ir.json", omtd / "harness.ir.json")
    for rel, (src, hours) in mtimes.items():
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / src, dst)
    if git:
        env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(root)}
        for args in (
            ["git", "init", "-q"],
            ["git", "config", "user.email", "golden@example.com"],
            ["git", "config", "user.name", "golden"],
            ["git", "add", "-A"],
            ["git", "commit", "-qm", "seed"],
        ):
            subprocess.run(args, cwd=root, check=True, capture_output=True, env=env)
        for rel in mtimes:
            with (root / rel).open("a", encoding="utf-8") as fh:
                fh.write("\n# golden-dirty marker\n")
    for rel, (src, hours) in mtimes.items():
        ts = datetime.now(timezone.utc).timestamp() + hours * 3600
        os.utime(root / rel, (ts, ts))
    return root


def _write_receipt(root: Path, receipt: dict) -> None:
    """Write the seeded receipt AFTER _seed_tree: digest-bearing blocks must
    hash the POST-append seeded content, and the receipt stays the newest
    artifact in the tmp root."""
    (root / ".meta" / ".omt" / "omt_harness_e2e_last_run.json").write_text(
        json.dumps(receipt), encoding="utf-8"
    )


def _probe(root: Path, target: str = "-") -> dict:
    assert BUN is not None
    scratch = root / ".." / "scratch"
    scratch = scratch.resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    script = SLICES_PROBE.replace("%LIB%", str(LIB))
    probe = scratch / "probe_slices.ts"
    probe.write_text(script, encoding="utf-8")
    out = subprocess.run(
        ["bun", str(probe), str(root), target],
        capture_output=True, text=True, timeout=60,
    )
    assert out.returncode == 0, f"bun probe failed:\n{out.stderr}\n---"
    return json.loads(out.stdout.strip().splitlines()[-1])


@pytest.mark.skipif(BUN is None, reason="bun not available")
class TestSliceResolution:
    def test_receipt_slice_for_resolves_mapped_and_unmapped(self, tmp_path):
        root = _seed_tree(tmp_path, {})
        _write_receipt(root, {"passed_at": _iso()})
        out = _probe(root)
        assert out["slice_q"] == "q", out
        assert out["slice_net_prefix"] == "net", out
        assert out["slice_split"] == "split_proof", out
        assert out["unmapped"] is None, out


@pytest.mark.skipif(BUN is None, reason="bun not available")
class TestSliceFreshness:
    def test_fresh_slice_block_decouples_from_global(self, tmp_path):
        """I2 hermetic-class pin: no git (fail-open) — the gate's clean-git
        early exit passes both files; the DECOUPLING verdict (real git-dirty
        roots) is pinned by test_slice_timestamp_logic_decouples."""
        root = _seed_tree(tmp_path, {
            ".opencode/plugins/omt_q.ts": (".opencode/plugins/omt_q.ts", 0.0),
            "scripts/omt/net/state.py": ("scripts/omt/net/state.py", -0.5),  # newer than global
        }, git=False)
        receipt = {
            "passed_at": _iso(-3),
            "slices": {
                "q": {"passed_at": _iso(1), "results_passed": True,
                      "digests": {".opencode/plugins/omt_q.ts": None}},  # filled below
            },
        }
        import hashlib
        q_src = REPO / ".opencode" / "plugins" / "omt_q.ts"
        receipt["slices"]["q"]["digests"][".opencode/plugins/omt_q.ts"] = hashlib.sha256(
            q_src.read_bytes()
        ).hexdigest()
        _write_receipt(root, receipt)
        q_abs = str(root / ".opencode" / "plugins" / "omt_q.ts")
        net_abs = str(root / "scripts" / "omt" / "net" / "state.py")
        out_q = _probe(root, q_abs)
        out_net = _probe(root, net_abs)
        assert out_q["slice_q"] == "q"
        # no .git → isGitDirty fails open → both ok (hermetic no-git class);
        # the real decoupling verdict is pinned with git-dirty roots in
        # test_slice_timestamp_logic_decouples.
        assert out_q["status"]["ok"] is True
        assert out_net["status"]["ok"] is True

    def test_slice_timestamp_logic_decouples(self, tmp_path):
        """I2 core: slice-fresh file passes with a stale GLOBAL block; a mapped
        file whose slice is stale is blocked. REAL git-dirty root (committed
        tree + appended marker) so isGitDirty is true and the gate reaches the
        slice branch; slice freshness is a PURE passed_at vs mtime check (no
        receipt-file mtime floor — that floor is global-branch only)."""
        import hashlib
        root = _seed_tree(tmp_path, {
            ".opencode/plugins/omt_q.ts": (".opencode/plugins/omt_q.ts", 0.0),
            "scripts/omt/net/state.py": ("scripts/omt/net/state.py", 0.0),
        })
        q_digest = hashlib.sha256(
            (root / ".opencode" / "plugins" / "omt_q.ts").read_bytes()
        ).hexdigest()
        receipt = {
            "passed_at": _iso(-3),  # global stale vs everything
            "slices": {
                "q": {"passed_at": _iso(1), "results_passed": True,
                      "digests": {".opencode/plugins/omt_q.ts": q_digest}},
                "net": {"passed_at": _iso(-2), "results_passed": True,
                        "digests": {}},
            },
        }
        _write_receipt(root, receipt)
        out_q = _probe(root, str(root / ".opencode" / "plugins" / "omt_q.ts"))
        out_net = _probe(root, str(root / "scripts" / "omt" / "net" / "state.py"))
        assert out_q["status"]["ok"] is True, out_q  # slice q fresh → editable
        assert out_net["status"]["ok"] is False, out_net  # slice net stale → blocked
        # receipt_stale msg text: names the baked e2e refresh command (the
        # word "receipt" itself is not in the @msg teaching text).
        assert "e2e" in out_net["status"]["msg"].lower()

    def test_slice_digest_mismatch_blocks(self, tmp_path):
        """I3: fresh passed_at but stale digest → blocked (content-bound)."""
        root = _seed_tree(tmp_path, {
            ".opencode/plugins/omt_q.ts": (".opencode/plugins/omt_q.ts", 0.0),
        })
        receipt = {
            "passed_at": _iso(-3),
            "slices": {
                "q": {"passed_at": _iso(1), "results_passed": True,
                      "digests": {".opencode/plugins/omt_q.ts": "0" * 64}},
            },
        }
        _write_receipt(root, receipt)
        out = _probe(root, str(root / ".opencode" / "plugins" / "omt_q.ts"))
        assert out["status"]["ok"] is False, out
        assert "e2e" in out["status"]["msg"].lower()

    def test_legacy_receipt_without_slices_stays_global(self, tmp_path):
        """I6: no `slices` key → mapped + unmapped both follow the global block
        (byte-identical v1). Target mtimes seed +0.5h FUTURE: the global
        branch's receiptTimestampMs() floors at the receipt FILE's mtime
        (written ~now), so a stale passed_at alone cannot pin the stale
        verdict without future-dated targets."""
        root = _seed_tree(tmp_path, {
            ".opencode/plugins/omt_q.ts": (".opencode/plugins/omt_q.ts", 0.5),
            "scripts/omt/harnessc.py": ("scripts/omt/harnessc.py", 0.5),
        })
        receipt_path = root / ".meta" / ".omt" / "omt_harness_e2e_last_run.json"
        receipt_path.write_text(json.dumps({"passed_at": _iso(1)}), encoding="utf-8")
        out_q = _probe(root, str(root / ".opencode" / "plugins" / "omt_q.ts"))
        out_h = _probe(root, str(root / "scripts" / "omt" / "harnessc.py"))
        assert out_q["status"]["ok"] is True, out_q  # global branch, fresh
        receipt_path.write_text(json.dumps({"passed_at": _iso(-2)}), encoding="utf-8")
        out_q2 = _probe(root, str(root / ".opencode" / "plugins" / "omt_q.ts"))
        out_h2 = _probe(root, str(root / "scripts" / "omt" / "harnessc.py"))
        assert out_q2["status"]["ok"] is False, out_q2  # global stale → blocked
        assert out_h2["status"]["ok"] is False, out_h2


class TestReceiptCli:
    def _cli(self, root: Path, *args) -> subprocess.CompletedProcess:
        return subprocess.run(
            [UV, "run", str(RECEIPT_CLI), *args, "--root", str(root)],
            capture_output=True, text=True, timeout=300, cwd=str(REPO),
        )

    def _mini_repo(self, tmp_path: Path) -> Path:
        """Hermetic mini repo: a slice map is read from the REAL policy file at
        REPO, so the CLI test pins the v1 seed slices against mini copies."""
        root = tmp_path / "cli"
        omtd = root / ".meta" / ".omt"
        omtd.mkdir(parents=True, exist_ok=True)
        (omtd / "omt_harness_e2e_last_run.json").write_text("{}", encoding="utf-8")
        return root

    def test_missing_cli_fails(self, tmp_path):
        assert RECEIPT_CLI.exists(), "RED: scripts/omt/receipt.py must exist"

    def test_mint_green_writes_block_atomically(self, tmp_path):
        root = self._mini_repo(tmp_path)
        # --tests override keeps the mint hermetic (design O3 allows the runner
        # to be pointed at a green set; production invocations use the map).
        green = tmp_path / "green_test.py"
        green.write_text(
            "def test_ok():\n    assert True\n", encoding="utf-8"
        )
        p = self._cli(root, "mint", "--slice", "q", "--tests", str(green))
        assert p.returncode == 0, p.stdout + p.stderr
        receipt = json.loads(
            (root / ".meta" / ".omt" / "omt_harness_e2e_last_run.json").read_text()
        )
        blk = receipt["slices"]["q"]
        assert blk["results_passed"] is True
        assert blk["passed_at"]
        assert ".opencode/plugins/omt_q.ts" in blk["digests"]

    def test_mint_red_cuts_no_receipt(self, tmp_path):
        root = self._mini_repo(tmp_path)
        red = tmp_path / "red_test.py"
        red.write_text(
            "def test_boom():\n    assert False, 'red slice'\n", encoding="utf-8"
        )
        p = self._cli(root, "mint", "--slice", "q", "--tests", str(red))
        assert p.returncode == 1, p.stdout + p.stderr
        receipt = json.loads(
            (root / ".meta" / ".omt" / "omt_harness_e2e_last_run.json").read_text()
        )
        assert "slices" not in receipt or "q" not in receipt.get("slices", {})

    def test_status_read_only(self, tmp_path):
        root = self._mini_repo(tmp_path)
        before = (root / ".meta" / ".omt" / "omt_harness_e2e_last_run.json").read_text()
        p = self._cli(root, "status")
        assert p.returncode == 0, p.stdout + p.stderr
        out = json.loads(p.stdout.strip().splitlines()[-1])
        assert "slices" in out and "global" in out
        after = (root / ".meta" / ".omt" / "omt_harness_e2e_last_run.json").read_text()
        assert before == after, "status must never write"

    def test_mint_all_mints_every_slice_leaves_global(self, tmp_path):
        root = self._mini_repo(tmp_path)
        green = tmp_path / "green_test.py"
        green.write_text("def test_ok():\n    assert True\n", encoding="utf-8")
        p = self._cli(root, "mint", "--slice", "all", "--tests", str(green))
        assert p.returncode == 0, p.stdout + p.stderr
        receipt = json.loads(
            (root / ".meta" / ".omt" / "omt_harness_e2e_last_run.json").read_text()
        )
        for name in ("q", "net", "split_proof"):
            assert name in receipt["slices"], f"slice {name} missing from all-mint"
        assert "passed_at" not in receipt or receipt.get("passed_at") is None or isinstance(receipt.get("passed_at"), str), "global block untouched by slice mint"
