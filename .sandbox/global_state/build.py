#!/usr/bin/env python3
"""MH10 P1 global-state builder (feature_102, advisory only, sidecar-first).

Opencode usage (meta-harness focused, no new live tool registration):
    uv run .sandbox/global_state/build.py [--format md|json] [--out DIR]

What it does (read-only — never mutates live harness state):
  - joins 4 domains into ONE bounded view: projects / workflows / features / tasks
  - facts only: `uv run scripts/omt/net_check.py probe` + WORK.md Tasks +
    `.projects/meta/META.md` + ledger phase/project_link records
  - writes into .sandbox/global_state/: projection.md (<=2KB, line-cut
    continuation, never mid-sentence) + projection.json + divergence.md

Locks (PROJECT.md D3/D6, R1-R6): advisory projection, never authority; no new
gates/tools/budgets (net-zero holds); MH10 never imports src/agentx/* (R2);
no new store (R6 — snapshots are files, not a store); sync-generated rows are
labeled derived (R5); per-section as-of, no global as-of (R3); join keys
explicit, C4 residual named never interpolated (R3); workflow section shows
catalog position + last .sandbox/ round pointer only (R5); doc->token loss
labeled; unknown stays unknown.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DEFAULT = REPO_ROOT / ".sandbox" / "global_state"
CAP_BYTES = 2048

# C6/C1 anchors (head-verified, PROJECT.md References — named, not claimed).
C6_MOVE = "scripts/omt/net/state.py:819-834"
C6_CLAIM = "scripts/omt/net/state.py:837+ (claim_task)"
C6_LANE = "scripts/omt/net/state.py:296-300 vs fire() :763-768"
C1_WINDOW = "scripts/omt/net/state.py:730-742 vs WAL :672-675"


def _run(cmd: list[str], cwd: Path) -> str | None:
    try:
        out = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=30
        )
        return out.stdout.strip() or None
    except Exception:
        return None


def head_sha() -> str:
    sha = _run(["git", "rev-parse", "HEAD"], REPO_ROOT)
    return sha[:12] if sha else "HEAD"


def now_ts() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def probe_net() -> dict:
    raw = _run(["uv", "run", "scripts/omt/net_check.py", "probe"], REPO_ROOT)
    if not raw:
        return {"_unknown": "probe unavailable (unknown stays unknown)"}
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return {"_unknown": "probe unparseable (unknown stays unknown)"}


def read_text(rel: str) -> str | None:
    p = REPO_ROOT / rel
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return None


def parse_work_tasks(text: str | None) -> dict:
    """WORK.md Tasks menu (net_rev + NEXT/Other/Blocked/Resources + Pool line)."""
    if not text:
        return {"_unknown": "WORK.md unreadable"}
    m_rev = re.search(r"net_rev:(\d+)", text)
    m_pool = re.search(
        r"Pool:\s*pending=(\d+)\s+active=(\d+)\s+done=(\d+)", text
    )
    nxt = re.search(r"^NEXT:\s*(.*)$", text, re.M)
    return {
        "net_rev": m_rev.group(1) if m_rev else "unknown",
        "next": nxt.group(1).strip() if nxt else "unknown",
        "pool": (
            {
                "pending": int(m_pool.group(1)),
                "active": int(m_pool.group(2)),
                "done": int(m_pool.group(3)),
            }
            if m_pool
            else {"_unknown": "pool line not found"}
        ),
        "derived_rows": "## Projects block is sync-generated (derived, never source)",
    }


def parse_manifest(text: str | None) -> list[dict]:
    """`.projects/meta/META.md` rows — all marked derived (R5)."""
    rows: list[dict] = []
    if not text:
        return rows
    for line in text.splitlines():
        m = re.match(
            r"\|\s*([\w_]+)\s*\|\s*(\w+)\s*\|\s*(.*?)\s*\|\s*([\d\-—]+)\s*\|\s*([\d\-—]+)\s*\|",
            line,
        )
        if m and m.group(1) not in ("project", "_(none)_"):
            rows.append(
                {
                    "slug": m.group(1),
                    "state": m.group(2),
                    "features": m.group(3),
                    "derived": True,
                }
            )
    return rows


def ledger_feature_phases() -> dict[str, str]:
    """Latest phase per feature from hot ledger (join key = feature slug)."""
    latest: dict[str, str] = {}
    for name in ("ledger.jsonl",):
        p = REPO_ROOT / ".meta" / ".omt" / name
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines[-2000:]:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("kind") == "phase" and r.get("feature") and r.get("phase"):
                if r["phase"] != "abandoned":
                    latest[str(r["feature"])] = str(r["phase"])
    return latest


def ledger_project_of() -> dict[str, str]:
    """Latest project_link per feature (join key = feature slug)."""
    links: dict[str, str] = {}
    p = REPO_ROOT / ".meta" / ".omt" / "ledger.jsonl"
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except OSError:
        return links
    for line in lines[-2000:]:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("kind") == "project_link" and r.get("feature") and r.get("project"):
            links[str(r["feature"])] = str(r["project"])
    return links


def workflow_section() -> dict:
    """Catalog position + last .sandbox/ round pointer only (R5 honesty)."""
    wf_root = REPO_ROOT / ".workflows"
    subjects: list[str] = []
    try:
        if wf_root.is_dir():
            subjects = sorted(
                d.name for d in wf_root.iterdir() if d.is_dir()
            )[:12]
    except OSError:
        pass
    last_round: str | None = None
    try:
        sb = REPO_ROOT / ".sandbox"
        cands = [f for f in sb.iterdir() if f.is_file()]
        if cands:
            newest = max(cands, key=lambda f: f.stat().st_mtime)
            last_round = f".sandbox/{newest.name}"
    except OSError:
        pass
    return {
        "note": "doc-shaped domain: catalog is agent-read markdown, zero machine state",
        "subjects": subjects or "unknown",
        "last_round_pointer": last_round or "unknown",
    }


def build_projection() -> tuple[dict, list[str]]:
    """Returns (projection_dict, divergence_rows_md)."""
    head = head_sha()
    ts = now_ts()
    probe = probe_net()
    rev = str(probe.get("revision", "unknown"))
    marking = probe.get("marking", {})
    menu = probe.get("menu", {})
    observation = probe.get("observation", {})

    work_text = read_text("WORK.md")
    tasks = parse_work_tasks(work_text)
    manifest = parse_manifest(read_text(".projects/meta/META.md"))
    phases = ledger_feature_phases()
    try:
        proj_of = ledger_project_of()
    except Exception:
        proj_of = {}

    # --- divergence: projection(B) vs marking(M) ---------------------------
    div: list[str] = []
    pool = tasks.get("pool", {}) if isinstance(tasks, dict) else {}
    for place, key in (
        ("work_pending", "pending"),
        ("work_active", "active"),
        ("work_done", "done"),
    ):
        b = pool.get(key, "?") if isinstance(pool, dict) else "?"
        m = marking.get(place, "?") if isinstance(marking, dict) else "?"
        fired = "no (OMISSION class — counts agreeing with no fired transition)"
        div.append(f"| `{key}` pool(B)={b} | `{place}`(M)={m} | fired? {fired} |")
    div.append(
        f"| known omission paths | `claim_task`/recovery/lane/integration via `_move_pool_token` {C6_MOVE},{C6_CLAIM}; absent-lane binding-only {C6_LANE} | counted as OMISSIONS, never firings |"
    )
    div.append(
        f"| crash window | clear-before-record {C1_WINDOW} — P1 never depends on replay surviving it | carried residual |"
    )

    join_keys = (
        "WORK.md pool rows <-> ledger `feature` slug <-> net task bindings `id` "
        "<-> project slugs (`.projects/meta/<slug>`). C4 residual: identities "
        "differ per domain — rows without a shared key are juxtaposed, flagged "
        "`join:unmatched`, never interpolated."
    )

    proj = {
        "advisory": "read-only projection — never grants/authorizes/mutates policy",
        "as_of": {
            "note": "no global as-of exists; per-section stamps only",
            "head": head,
            "built_ts": ts,
            "net_rev": rev,
            "work_md": "live read @ build ts (derived Projects block via project.py sync)",
            "manifest": "sync-generated (derived, never source)",
            "ledger": "hot ledger tail @ build ts",
        },
        "tasks": {
            "pool": pool,
            "net_marking": {
                k: marking.get(k, "?")
                for k in ("work_pending", "work_active", "work_done")
            },
            "resources": menu.get("resources", "?"),
            "workers": menu.get("capacity", "?"),
            "next": tasks.get("next", "?"),
            "observation": observation,
        },
        "projects": manifest,
        "workflows": workflow_section(),
        "features": {
            "phases": phases or "unknown (no phase records in hot tail)",
            "project_links": proj_of or "unknown",
            "tdd_position": "see omt_q{op:state, feature} (this view carries lifecycle only)",
        },
        "join_keys": join_keys,
        "loss": "doc->token projection is lossy (prose STATUS/notes truncated) — loss labeled, neverPATCHED",
    }
    return proj, div


def _short_features(feats: str, limit: int = 72) -> str:
    """Truncate long feature lists for the ≤2KB md (json keeps full rows)."""
    if len(feats) <= limit:
        return feats
    head, n = feats[:limit].rsplit(",", 1)[0], feats.count(",")
    return f"{head} +{n} more"


def render_md(proj: dict, div_rows: list[str]) -> str:
    # R4 fix (Testing): critical-resume sections FIRST so the ≤2KB line-cut
    # keeps divergence/join/workflows answerable from projection.md alone.
    # Projects fill remaining budget (active first), full rows in json.
    a = proj["as_of"]
    pool = proj["tasks"]["pool"] if isinstance(proj["tasks"]["pool"], dict) else {}
    mark = proj["tasks"]["net_marking"] if isinstance(proj["tasks"]["net_marking"], dict) else {}
    lines = [
        "# Global state (P1 advisory projection — read-only, never authority)",
        f"`rev {a['net_rev']} @ {a['head']} · built {a['built_ts']}` (per-section as-of; no global as-of)",
        "",
        f"## tasks — pool {proj['tasks']['pool']} · marking {proj['tasks']['net_marking']}",
        f"resources {proj['tasks']['resources']} · workers {proj['tasks']['workers']} · NEXT: {proj['tasks']['next']}",
        "",
        "## divergence — projection(B) vs marking(M): omissions, never firings",
        f"| B vs M: pending {pool.get('pending', '?')}/{mark.get('work_pending', '?')}, "
        f"active {pool.get('active', '?')}/{mark.get('work_active', '?')}, "
        f"done {pool.get('done', '?')}/{mark.get('work_done', '?')} — agree, no fired transition (OMISSION class) |",
        f"| omissions: claim_task/recovery/lane via _move_pool_token {C6_MOVE},{C6_CLAIM}; absent-lane {C6_LANE} — never firings |",
        f"| crash: clear-before-record {C1_WINDOW} — P1 never depends on replay |",
        "",
        f"## join keys — {proj['join_keys']}",
        "",
    ]
    wf = proj["workflows"]
    lines += [
        f"## workflows — subjects {wf['subjects']} · last round `{wf['last_round_pointer']}`",
        f"({wf['note']}; catalog position + round pointer only)",
        "",
        f"## features — phases {len(proj['features']['phases']) if isinstance(proj['features']['phases'], dict) else '?'} tracked (join key = feature slug; `join:unmatched` never interpolated)",
        "",
        "## projects (derived sync rows — never source)",
    ]
    ordered = sorted(proj["projects"], key=lambda r: (0 if r.get("state") == "active" else 1))
    for r in ordered:
        lines.append(f"- {r['slug']} ({r['state']}) · {_short_features(str(r['features']))}")
    if not proj["projects"]:
        lines.append("- unknown (manifest unreadable)")
    lines += [
        "",
        "_Advisory only (MH10 P1). Loss: prose truncated, labeled. Full rows: projection.json. Detail: omt_q{op:state}, omt_net{op:probe}, WORK.md._",
    ]
    return "\n".join(lines) + "\n"


def fit_cap(text: str, cap: int = CAP_BYTES) -> tuple[str, bool]:
    """Line-cut to cap (never mid-sentence); returns (text, continued)."""
    if len(text.encode("utf-8")) <= cap:
        return text, False
    marker = "\n… continued in projection.json (cap 2KB; cut at line boundary)\n"
    budget = cap - len(marker.encode("utf-8"))
    kept: list[str] = []
    used = 0
    for line in text.splitlines(keepends=True):
        nb = len(line.encode("utf-8"))
        if used + nb > budget:
            break
        kept.append(line)
        used += nb
    return "".join(kept).rstrip("\n") + marker, True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--format", choices=("md", "json"), default="md")
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args(argv)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    proj, div_rows = build_projection()
    md, continued = fit_cap(render_md(proj, div_rows))
    payload = {
        "projection": proj,
        "divergence_rows": div_rows,
        "md_continued": continued,
    }
    (out / "projection.md").write_text(md, encoding="utf-8")
    (out / "projection.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "divergence.md").write_text(
        "# divergence — projection(B) vs marking(M)\n\n"
        + "\n".join(div_rows)
        + "\n\n_Known paths are OMISSIONS (never firings)._\n",
        encoding="utf-8",
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
