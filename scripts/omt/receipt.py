#!/usr/bin/env python3
"""feature_151 T5 — per-mechanic receipt slice mint CLI (harness_wrapper_split).

Mints per-slice blocks into the shared e2e receipt JSON
(.meta/.omt/omt_harness_e2e_last_run.json):

  uv run scripts/omt/receipt.py mint --slice q [--tests PATH] [--root R] [--dry-run]
  uv run scripts/omt/receipt.py status [--root R]

- Slice map: the REAL policy manifest at REPO/.meta/templates/receipt_slices.json
  (@var receipt_slices_path); --root only gates the receipt path + digest
  targets, NEVER the pytest cwd (uv needs the repo project — tests always run
  with cwd=REPO, per the T5 design/operation spec).
- Fail-closed (I4): any red test in the slice set → exit 1, receipt untouched.
- Atomic merge (I5, GOTCHA_RECEIPT_ATOMIC_MINT): tmp file + os.replace.
- --slice all: mints every slice block; NEVER touches the legacy global block
  (the e2e test owns the global mint).
- status: read-only {global, slices} summary; never writes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO / ".meta" / "templates" / "receipt_slices.json"
RECEIPT_REL = ".meta/.omt/omt_harness_e2e_last_run.json"
UV = shutil.which("uv") or "uv"
TEST_TIMEOUT_S = 600


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        print(f"receipt.py: slice manifest missing: {MANIFEST_PATH}", file=sys.stderr)
        raise SystemExit(2)
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data:
        print(f"receipt.py: slice manifest empty: {MANIFEST_PATH}", file=sys.stderr)
        raise SystemExit(2)
    return data


def digest_of(root: Path, rel: str) -> str:
    """sha256 of root/<rel>; missing file → "" (never blocks on absence)."""
    try:
        return hashlib.sha256((root / rel).read_bytes()).hexdigest()
    except OSError:
        return ""


def read_receipt(root: Path) -> dict:
    try:
        data = json.loads((root / RECEIPT_REL).read_text(encoding="utf-8") or "{}")
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def write_receipt_atomic(root: Path, receipt: dict) -> None:
    """GOTCHA_RECEIPT_ATOMIC_MINT: tmp + os.replace — never a partial write."""
    p = root / RECEIPT_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".receipt_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(receipt, fh, indent=2)
            fh.write("\n")
        os.replace(tmp, p)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def run_tests(test_paths: list[str]) -> bool:
    """Run the slice's pytest set with cwd=REPO (NEVER --root — uv needs the
    repo project; --root only gates receipt path + digest targets)."""
    cmd = [UV, "run", "pytest", *test_paths, "-q"]
    try:
        proc = subprocess.run(cmd, cwd=str(REPO), timeout=TEST_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        print(
            f"receipt.py: slice tests timed out after {TEST_TIMEOUT_S}s: {test_paths}",
            file=sys.stderr,
        )
        return False
    return proc.returncode == 0


def cmd_mint(slice_name: str, tests_override: str | None, root: Path, dry_run: bool) -> int:
    manifest = load_manifest()
    if slice_name == "all":
        names = sorted(manifest.keys())
    elif slice_name in manifest:
        names = [slice_name]
    else:
        print(
            f"receipt.py: unknown slice {slice_name!r} (have: {', '.join(sorted(manifest))})",
            file=sys.stderr,
        )
        return 2
    # Fail-closed (I4): run EVERY slice's tests before writing anything — a
    # red slice cuts no receipt at all, not even the other slices' blocks.
    ran: dict[str, list[str]] = {}
    for name in names:
        spec = manifest[name] or {}
        test_paths = [tests_override] if tests_override else list(spec.get("tests") or [])
        if not test_paths:
            print(f"receipt.py: slice {name!r} has no tests", file=sys.stderr)
            return 2
        if not run_tests(test_paths):
            print(
                f"receipt.py: slice {name!r} tests RED — receipt untouched (fail-closed)",
                file=sys.stderr,
            )
            return 1
        ran[name] = test_paths
    now = datetime.now(timezone.utc).isoformat()
    receipt = read_receipt(root)
    slices = receipt.setdefault("slices", {})
    for name in names:
        spec = manifest[name] or {}
        digests = {rel: digest_of(root, rel) for rel in (spec.get("files") or [])}
        slices[name] = {"passed_at": now, "results_passed": True, "digests": digests}
    if dry_run:
        print(json.dumps({"dry_run": True, "slice": slice_name,
                          "slices": {n: slices[n] for n in names},
                          "tests": ran}))
        return 0
    write_receipt_atomic(root, receipt)
    print(json.dumps({"slice": slice_name, "passed_at": now, "tests": ran}))
    return 0


def cmd_status(root: Path) -> int:
    receipt = read_receipt(root)
    global_passed_at = receipt.get("passed_at") or "absent"
    per = {}
    for name, block in (receipt.get("slices") or {}).items():
        if not isinstance(block, dict):
            continue
        per[name] = {
            "passed_at": block.get("passed_at") or "absent",
            "results_passed": bool(block.get("results_passed")),
            "digests": len(block.get("digests") or {}),
        }
    print(json.dumps({"global": global_passed_at, "slices": per}))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="receipt.py",
        description="Per-mechanic receipt slice mint CLI (feature_151 T5).",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("mint", help="run slice tests and mint slice receipt block(s)")
    m.add_argument("--slice", required=True, help="slice name or 'all'")
    m.add_argument("--tests", default=None, help="override the slice's test set (hermetic hook)")
    m.add_argument("--root", default=str(REPO),
                   help="repo root gating the receipt path + digest targets")
    m.add_argument("--dry-run", action="store_true",
                   help="run tests and print blocks without writing")
    s = sub.add_parser("status", help="print global + per-slice receipt state (read-only)")
    s.add_argument("--root", default=str(REPO), help="repo root gating the receipt path")
    args = ap.parse_args(argv)
    if args.cmd == "mint":
        return cmd_mint(args.slice, args.tests, Path(args.root).resolve(), args.dry_run)
    if args.cmd == "status":
        return cmd_status(Path(args.root).resolve())
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
