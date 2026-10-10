#!/usr/bin/env python3
"""split_proof oracle, firewall slice (feature_138).

Advisory CLI only (`reason_check` precedent — zero registry rows, no `omt_`
prefix). Turns the V7 orthogonality claims into deterministic certificates:
AST import firewall (Python `ast` + TS imports, never substring) with a
versioned exemption manifest, plus a newcomer REPL probe (the AgentX-vision
guard). CI-strict / local-advisory; v1 scans the current tree (worktree
overlay lands with T3).

Deviation log (honesty over plan):
- `prove` runs the firewall scans only; the REPL boot lives in
  `newcomer-probe` (keeps `prove` fast and deterministic).
- `newcomer-probe` sends `help`, not `c`: the 0.2.0 console is a command
  REPL (`help` + Ctrl+C/EOF to exit) — single letters answer
  "Unknown command" (observed 2026-10-10). The V7 "`c`" narrative rotted;
  this probe guards what the console IS (boot + answer + clean exit).
- E3 (close-out): `prove` appends one `split_proof.cert` row per cert and
  `attest-bridge` one `split_proof.attest` row (chain: cert_sha + lane +
  prev ledger_sha; kinds extend, schema doesn't — A9: no kind validation,
  `net_*`-filtered readers never see them). `--ledger` overrides the chain
  file (hermetic tests pass tmp; missing = empty-chain genesis). `verify`
  re-proves read-only (`record=False`); self-append growth lands in the
  STALE-valid prefix branch, never a mismatch. `verify` on a quiet ledger
  now reports STALE-valid instead of byte-identical whenever a chain row
  landed since the cut — honest (the ledger DID grow, by our own row).
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ORACLE = "split_proof/v1"
KIND_CERT = "split_proof.cert"
KIND_ATTEST = "split_proof.attest"
GENESIS_SHA = hashlib.sha256(b"").hexdigest()
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

REPO = Path(__file__).resolve().parents[2]
MANIFEST_DEFAULT = REPO / "scripts" / "omt" / "split_proof_exemptions.json"

# Absolute-import prefixes that count as a runtime edge (relative imports
# — `from .x import ...` — never count; fixture/path STRINGS never count
# because the AST never sees them).
FWD_PREFIXES = ("scripts", "opencode")  # product -> harness
REV_PREFIXES = ("src.agentx", "agentx")  # harness -> product
TS_FORBIDDEN = ("src/agentx", "scripts/omt", ".meta/")
TS_IMPORT_RE = re.compile(
    r"^\s*(?:import\s+(?:[^'\"]*?\sfrom\s+)?|export\s+[^'\"]*?\sfrom\s+|import\s*)"
    r"['\"]([^'\"]+)['\"]"
)
CONFORMING_BRIDGE_RE = re.compile(r"^([-*]\s+)?(`?)bridge:\2(\s|$)")


def _hit(mod: str, prefixes: tuple[str, ...]) -> bool:
    return any(mod == p or mod.startswith(p + ".") for p in prefixes)


def find_runtime_imports(pyfile: Path, direction: str) -> list[str]:
    """Absolute runtime imports in one file, filtered by boundary direction."""
    prefixes = FWD_PREFIXES if direction == "product_to_harness" else REV_PREFIXES
    try:
        tree = ast.parse(pyfile.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return []
    edges: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                continue  # relative import — same package, not a boundary edge
            mods = [node.module] if node.module else []
        else:
            continue
        for mod in mods:
            if _hit(mod, prefixes):
                edges.append(f"{pyfile}:{getattr(node, 'lineno', '?')}: imports {mod}")
    return edges


def raw_hits(pyfile: Path, needle: str = "agentx") -> list[str]:
    """Substring occurrences (the false-positive class a naive golden trips on)."""
    try:
        lines = pyfile.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    return [f"{pyfile}:{i}" for i, ln in enumerate(lines, 1) if needle in ln]


def _exempt_lines(manifest: dict, rel: str) -> set[int]:
    return {
        e["line"]
        for e in manifest.get("python_exemptions", [])
        if e["file"] == rel
    }


def _py_files(base: Path) -> list[Path]:
    if not base.is_dir():
        return []
    return sorted(p for p in base.rglob("*.py") if ".venv" not in p.parts)


def scan_firewall(manifest_path: Path, root: Path) -> dict:
    """AST both-directions scan + pinned-substring exact-set check.

    Returns {"edges", "exempted", "files_scanned"}. Clean iff edges == [].
    The manifest stays live: every `agentx` substring line in an exempted
    file must be pinned (no more, no fewer), and each pinned line must still
    be a non-import (string), so converting a fixture into a real import
    fails loudly instead of slipping the firewall.
    """
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    edges: list[str] = []
    scanned = 0
    for rel_dir, direction in (("src/agentx", "product_to_harness"), ("scripts", "harness_to_product")):
        for py in _py_files(root / rel_dir):
            scanned += 1
            edges.extend(find_runtime_imports(py, direction))
    exempted = 0
    pinned_files = {e["file"] for e in manifest.get("python_exemptions", [])}
    for rel in sorted(pinned_files):
        f = root / rel
        actual = {int(h.rsplit(":", 1)[1]) for h in raw_hits(f)}
        want = _exempt_lines(manifest, rel)
        if actual != want:
            edges.append(
                f"{rel}: exemption drift — actual agentx lines {sorted(actual)} "
                f"!= pinned {sorted(want)} (re-pin the manifest, never weaken the scan)"
            )
        else:
            # Each pinned line must still be a non-import (string, not code).
            tree = ast.parse(f.read_text(encoding="utf-8"))
            import_lines = {
                getattr(n, "lineno", -1)
                for n in ast.walk(tree)
                if isinstance(n, (ast.Import, ast.ImportFrom))
            }
            for ln in want:
                if ln in import_lines:
                    edges.append(f"{rel}:{ln}: pinned string became a real import")
            exempted += len(want)
    return {"edges": sorted(edges), "exempted": exempted, "files_scanned": scanned}


def scan_ts_firewall(manifest_path: Path, root: Path) -> dict:
    """TS import-specifier scan over the studio tree (relative imports pass)."""
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    exempt = set(manifest.get("ts_exemptions", []))
    edges: list[str] = []
    scanned = 0
    base = root / "tools" / "petri-net-studio"
    for sub in ("src", "tests"):
        d = base / sub
        if not d.is_dir():
            continue
        for ts in sorted(d.rglob("*.ts")) + sorted(d.rglob("*.tsx")):
            scanned += 1
            try:
                lines = ts.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            for i, ln in enumerate(lines, 1):
                m = TS_IMPORT_RE.match(ln)
                if not m:
                    continue
                spec = m.group(1)
                if spec.startswith((".", "/")):
                    continue
                if any(s in spec for s in TS_FORBIDDEN) and f"{ts}:{i}" not in exempt:
                    edges.append(f"{ts}:{i}: TS imports {spec}")
    return {"edges": sorted(edges), "files_scanned": scanned}


def _ta_hash(root: Path) -> str:
    counts: list[str] = []
    base = root / "src" / "agentx"
    if base.is_dir():
        for py in sorted(base.rglob("*.py")):
            try:
                n = sum(
                    1
                    for ln in py.read_text(encoding="utf-8").splitlines()
                    if re.match(r"\s*#\s*TA:", ln)
                )
            except OSError:
                n = 0
            if n:
                counts.append(f"{py.relative_to(root)}:{n}")
    return hashlib.sha256("\n".join(counts).encode()).hexdigest()


def _revs(root: Path) -> tuple[str, str]:
    file_rev = "unknown"
    try:
        m = re.search(
            r"net_rev:(\d+)", (root / "WORK.compiled.md").read_text(encoding="utf-8")
        )
        if m:
            file_rev = m.group(1)
    except OSError:
        pass
    live_rev = "unknown"
    try:
        live_rev = str(
            json.loads(
                (root / ".meta" / ".omt" / "net_state.sidecar.json").read_text(
                    encoding="utf-8"
                )
            ).get("revision", "unknown")
        )
    except OSError:
        pass
    return file_rev, live_rev


def _ledger_path(root: Path, override: str | None) -> Path:
    if override:
        return Path(override)
    return root / ".meta" / ".omt" / "ledger.jsonl"


def _ledger_sha(ledger: Path) -> str:
    # E3: missing ledger = empty-chain genesis (hermetic `--ledger` tmp files
    # start nonexistent; the first append creates them). The real ledger
    # always exists, so genesis never masks a typo'd live path in practice.
    try:
        return hashlib.sha256(ledger.read_bytes()).hexdigest()
    except OSError:
        return GENESIS_SHA


def _append_ledger_row(ledger: Path, record: dict) -> None:
    """Append one flat record, `ts`-stamped (A9: no kind validation — new
    kinds flow; `net_*`-filtered readers never see `split_proof.*`)."""
    ledger.parent.mkdir(parents=True, exist_ok=True)
    row = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()), **record}
    with open(ledger, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def check_cert_sha(data: dict) -> bool:
    """Recompute the chain hash (payload minus `cert_sha` itself)."""
    payload = {k: data[k] for k in LOCKED_FIELDS if k != "cert_sha"}
    canon = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canon.encode()).hexdigest() == data.get("cert_sha")


def prove_lane(
    lane: str,
    manifest_path: Path,
    root: Path,
    out_dir: Path,
    ledger: Path,
    record: bool = True,
) -> Path:
    """Run the scans, emit one LOCKED cert (≤2 KiB).

    E3: when `record`, append one `split_proof.cert` row (cert_sha + lane +
    prev ledger_sha chain link) AFTER the cert is cut — so the cert's own
    `ledger_sha` is the pre-append state and the row chains it forward.
    `verify` re-proves with `record=False` (read-only compare, no chain
    spam); any residual sha drift falls through to the STALE-valid prefix
    check, which stays honest because our own rows are append-only growth.
    """
    t0 = time.monotonic()
    fw = scan_firewall(manifest_path, root)
    ts = scan_ts_firewall(manifest_path, root)
    edges = fw["edges"] + ts["edges"]
    file_rev, live_rev = _revs(root)
    prev_sha = _ledger_sha(ledger)
    cert = {
        "oracle": ORACLE,
        "lane": lane,
        "file_rev": file_rev,
        "live_rev": live_rev,
        "ledger_sha": prev_sha,
        "firewall_verdict": "clean" if not edges else f"VIOLATION:{len(edges)}",
        "ta_ast_hash": _ta_hash(root),
        "newcomer": "not-run",
        "tokens_ms": int((time.monotonic() - t0) * 1000),
        "cert_sha": "",
    }
    canon = json.dumps(
        {k: cert[k] for k in LOCKED_FIELDS if k != "cert_sha"},
        separators=(",", ":"),
        ensure_ascii=True,
    )
    cert["cert_sha"] = hashlib.sha256(canon.encode()).hexdigest()
    raw = json.dumps(cert, separators=(",", ":")).encode()
    assert len(raw) <= 2048, f"cert exceeds 2 KiB: {len(raw)}"
    if edges:
        raise SystemExit(f"firewall VIOLATION ({len(edges)} edges):\n" + "\n".join(edges))
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"split_proof_{lane}.cert.json"
    dest.write_bytes(raw)
    print(f"prove:{lane}: clean files={fw['files_scanned']}+{ts['files_scanned']} "
          f"exempted={fw['exempted']} cert={dest.name} sha={cert['cert_sha'][:12]}")
    if record:
        _append_ledger_row(ledger, {
            "kind": KIND_CERT,
            "oracle": ORACLE,
            "lane": lane,
            "cert_sha": cert["cert_sha"],
            "ledger_sha": prev_sha,
        })
    return dest


def _ledger_prefix_match(want_sha: str, ledger: Path) -> int | None:
    """Return the row count K if `want_sha` is the sha256 of a K-line prefix
    of the current ledger (append-only growth), else None. K=0 (empty-chain
    genesis) counts: a cert cut against a fresh hermetic `--ledger` stays
    provenance-valid after its own chain row lands."""
    try:
        raw = ledger.read_bytes()
    except OSError:
        return None
    # Genesis certs (cut against a missing/empty hermetic ledger) are intact
    # by `check_cert_sha` before we get here — forging `ledger_sha` breaks
    # `cert_sha` first — so GENESIS always means "empty chain at cut", row 0.
    # (A live cert never carries GENESIS: the real ledger is never empty.)
    if want_sha == GENESIS_SHA:
        return 0
    if hashlib.sha256(raw).hexdigest() == want_sha:
        return len(raw.splitlines())
    acc = b""
    for i, line in enumerate(raw.splitlines(keepends=True), 1):
        acc += line if line.endswith(b"\n") else line + b"\n"
        if hashlib.sha256(acc).hexdigest() == want_sha:
            return i
    return None


def verify_cert(
    cert_path: Path, manifest_path: Path, root: Path, ledger: Path, attempts: int = 3
) -> None:
    """Re-prove the lane; assert byte-identical modulo `tokens_ms`.

    The `ledger_sha` chain link binds the ledger state at prove time, but the
    suite itself appends real ledger rows on parallel workers (observed
    2026-10-10: `ledger.jsonl` grows during `pytest tests/scripts/omt`), so a
    single compare is racy. Retry up to `attempts` times: pass on the first
    agreeing pair. If fresh proves agree with each other but not the given
    cert, the cert is STALE (ledger advanced since it was cut — re-prove),
    which is reported distinctly from a mismatch (tamper/drift).
    """
    data = json.loads(Path(cert_path).read_text(encoding="utf-8"))
    if not check_cert_sha(data):
        raise SystemExit(f"verify: cert_sha MISMATCH in {cert_path.name}")
    for _ in range(attempts):
        with tempfile.TemporaryDirectory() as tmp:
            prove_lane(data["lane"], manifest_path, root, Path(tmp), ledger,
                       record=False)
            other = json.loads(
                (Path(tmp) / f"split_proof_{data['lane']}.cert.json").read_bytes()
            )
        if all(
            data[k] == other[k]
            for k in LOCKED_FIELDS
            if k not in ("cert_sha", "tokens_ms")
        ):
            print(f"verify: {Path(cert_path).name} byte-identical (minus tokens_ms)")
            return
        # Ledger-only growth? The cert stays PROVENANCE-VALID if its ledger_sha
        # is a prefix of today's ledger and every other field still agrees.
        if all(
            data[k] == other[k]
            for k in LOCKED_FIELDS
            if k not in ("cert_sha", "tokens_ms", "ledger_sha")
        ):
            rows = _ledger_prefix_match(data["ledger_sha"], ledger)
            if rows is not None:
                print(
                    f"verify: {Path(cert_path).name} STALE-valid "
                    f"(cut at ledger row {rows}; ledger only grew since — re-prove "
                    "for a fresh chain link)"
                )
                return
    raise SystemExit(f"verify: field drift in {Path(cert_path).name} (see fresh proves)")


def attest_bridge(root: Path) -> dict:
    """Conforming `bridge:` tags (standalone token) vs prose mentions."""
    conforming = 0
    prose: list[str] = []
    for proj in sorted((root / ".projects").rglob("PROJECT.md")):
        try:
            lines = proj.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        in_decisions = False
        for i, ln in enumerate(lines, 1):
            if ln.startswith("## "):
                in_decisions = "decision" in ln.lower()
            if "bridge:" not in ln:
                continue
            rel = f"{proj.relative_to(root)}:{i}:{ln.strip()}"
            if CONFORMING_BRIDGE_RE.match(ln.strip()) and in_decisions:
                conforming += 1
            else:
                prose.append(rel)
    return {"conforming": conforming, "prose_hits": prose}


def newcomer_probe(root: Path, timeout: int = 120) -> None:
    """Boot the console, ask for help, exit on EOF — zero harness knowledge."""
    p = subprocess.run(
        ["uv", "run", "agentx"],
        input="help\n",
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(root),
    )
    out = p.stdout or ""
    if p.returncode != 0:
        raise SystemExit(f"newcomer-probe: FAIL (exit {p.returncode}): {p.stderr[-2000:]}")
    if "agent" not in out.lower() or not out.strip():
        raise SystemExit("newcomer-probe: FAIL (no REPL answer)")
    print(f"newcomer-probe: pass ({len(out.strip().splitlines())} answer lines)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="split_proof oracle (advisory)")
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--manifest", default=str(MANIFEST_DEFAULT))
    sub = ap.add_subparsers(dest="verb", required=True)

    p = sub.add_parser("prove")
    p.add_argument("--lane", choices=["product", "harness", "both"], default="both")
    p.add_argument("--out", default=".")
    p.add_argument("--ledger", default=None)

    v = sub.add_parser("verify")
    v.add_argument("cert")
    v.add_argument("--ledger", default=None)

    a = sub.add_parser("attest-bridge")
    a.add_argument("--ledger", default=None)
    sub.add_parser("newcomer-probe")

    args = ap.parse_args(argv)
    root = Path(args.root)
    manifest = Path(args.manifest)
    # `--ledger` lives on prove/verify/attest-bridge (after the verb);
    # newcomer-probe never touches the ledger.
    ledger = _ledger_path(root, getattr(args, "ledger", None))
    try:
        if args.verb == "prove":
            lanes = ["product", "harness"] if args.lane == "both" else [args.lane]
            for lane in lanes:
                prove_lane(lane, manifest, root, Path(args.out), ledger)
        elif args.verb == "verify":
            verify_cert(Path(args.cert), manifest, root, ledger)
        elif args.verb == "attest-bridge":
            rep = attest_bridge(root)
            print(json.dumps(rep, indent=2))
            _append_ledger_row(ledger, {
                "kind": KIND_ATTEST,
                "oracle": ORACLE,
                "conforming": rep["conforming"],
                "prose_count": len(rep["prose_hits"]),
                "ledger_sha": _ledger_sha(ledger),
            })
        elif args.verb == "newcomer-probe":
            newcomer_probe(root)
    except SystemExit as e:
        msg = str(e)
        if msg:
            print(msg, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
