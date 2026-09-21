#!/usr/bin/env python3
"""toolbox CLI — T4 docs+tiers: query/list/show/sync + metered run/stats/lint + propose/approve/reject/promote/prune + docs/tiers."""
import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "toolbox" / "index.sqlite3"
SCHEMA = ROOT / "toolbox" / "schema.sql"
INDEX_JSON = ROOT / "toolbox" / "index.json"

CATEGORIES = [
    ("git", "Git state", "porcelain status / log recipes"),
    ("ledger", "Ledger slices", "ledger.jsonl window/drift recipes"),
    ("harness", "Harness budgets", "harnessc / nav recipes"),
    ("text", "Text utils", "json / frontmatter recipes"),
    ("session", "Session notes", "pause / resume recipes"),
]

SEEDS = [
    ("git.status_summary", "status_summary", "git",
     "toolbox/git/status_summary/run.sh", "toolbox/git/status_summary/main.py",
     "git porcelain status + branch summary", "git,status,dirty,porcelain"),
    ("ledger.window_slice", "window_slice", "ledger",
     "toolbox/ledger/window_slice/run.sh", "toolbox/ledger/window_slice/main.py",
     "slice last N ledger.jsonl lines with optional kind filter", "ledger,slice,tail,history"),
    ("harness.budget_check", "budget_check", "harness",
     "toolbox/harness/budget_check/run.sh", "toolbox/harness/budget_check/main.py",
     "wrap harnessc check budgets green", "harness,budget,check,limits"),
    ("text.json_split", "json_split", "text",
     "toolbox/text/json_split/run.sh", "toolbox/text/json_split/main.py",
     "split JSON-array or bullet/newline prose behaviors", "json,split,tdd,behaviors,prose"),
    ("session.pause_note_append", "pause_note_append", "session",
     "toolbox/session/pause_note_append/run.sh", "toolbox/session/pause_note_append/main.py",
     "stage a pause note entry (dry-run default)", "session,pause,note,resume"),
]

# T4 tier map (proposal §3f + §10): Tier-1 gets the 5 rehomed core tools,
# Tier-2/3 get the full set (all non-deprecated, incl. promoted). Mirrors
# harnessc TEMPLATE_TIERS (1 core, 2 long-lived, 3 full+receipt) without
# editing harnessc.py — toolbox tiering is policy (filter), not new gates.
TIER1_CORE = (
    "git.status_summary",
    "ledger.window_slice",
    "harness.budget_check",
    "text.json_split",
    "session.pause_note_append",
)

DOC_PATHS = (
    "toolbox/categories.md",
    "toolbox/tools.md",
    "toolbox/STARTUP_SNIPPET.txt",
    "toolbox/ONBOARDING.md",
)


def tier_filter_ids(tier):
    """Return allowed tool-id set for tier, or None for full set.

    tier 0/None = all non-deprecated; 1 = TIER1_CORE only; 2/3 = full set.
    Raises SystemExit(2) on unknown tier (CLI fail-closed).
    """
    if tier in (None, 0):
        return None
    if tier == 1:
        return set(TIER1_CORE)
    if tier in (2, 3):
        return None
    print(f"unknown tier {tier!r} (want 1|2|3)", file=sys.stderr)
    raise SystemExit(2)


def apply_tier(rows, tier):
    allowed = tier_filter_ids(tier)
    if allowed is None:
        return list(rows)
    return [r for r in rows if r["id"] in allowed]


def db_connect():
    if not DB.exists():
        print(f"missing DB {DB} — run `toolbox.py sync` first", file=sys.stderr)
        raise SystemExit(1)
    con = sqlite3.connect(str(DB))
    con.row_factory = sqlite3.Row
    return con


def cmd_query(args):
    con = db_connect()
    q = args.keywords.strip().lower()
    toks = [t for t in q.split() if t]
    rows = con.execute("SELECT * FROM tools WHERE deprecated_by IS NULL").fetchall()
    rows = apply_tier(rows, getattr(args, "tier", 0) or 0)
    scored = []
    for r in rows:
        hay = f"{r['id']} {r['name']} {r['category']} {r['description']} {r['tags']}".lower()
        if not toks:
            score = 1
        else:
            score = 0
            for t in toks:
                if t in r["id"].lower():
                    score += 3
                elif t in r["name"].lower():
                    score += 2
                elif t in hay:
                    score += 1
                else:
                    score -= 1
        if not toks or score > 0:
            scored.append((score, (r["uses"] or 0), r))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    top = scored[: args.limit]
    if args.format == "json":
        print(json.dumps({"ok": True, "data": [dict(r) for _, _, r in top]}, indent=2))
    else:
        for score, _, r in top:
            print(f"{r['id']} [{r['category']}] — {r['description']} (score={score} uses={r['uses']})")
    con.close()


def cmd_list(args):
    con = db_connect()
    tier = getattr(args, "tier", 0) or 0
    tier_filter_ids(tier)  # fail-closed on bad tier even when category set
    if args.category:
        rows = con.execute(
            "SELECT * FROM tools WHERE category=? AND deprecated_by IS NULL ORDER BY id", (args.category,)
        ).fetchall()
    else:
        rows = con.execute("SELECT * FROM tools ORDER BY category, id").fetchall()
        rows = [r for r in rows if r["deprecated_by"] is None]
    rows = apply_tier(rows, tier)
    if args.format == "json":
        print(json.dumps({"ok": True, "data": [dict(r) for r in rows]}, indent=2))
    else:
        for r in rows:
            print(f"{r['id']} [{r['category']}] — {r['description']}")
    con.close()


def cmd_show(args):
    con = db_connect()
    r = con.execute("SELECT * FROM tools WHERE id=?", (args.tool_id,)).fetchone()
    con.close()
    if not r:
        print(json.dumps({"ok": False, "error": f"unknown tool {args.tool_id}"}))
        raise SystemExit(1)
    doc = ROOT / r["bash_entry"].replace("/run.sh", "/TOOL.md")
    body = doc.read_text() if doc.exists() else "(missing TOOL.md)"
    if args.format == "json":
        d = dict(r)
        d["tool_md"] = body
        print(json.dumps({"ok": True, "data": d}, indent=2))
    else:
        print(f"id: {r['id']}\ncategory: {r['category']}\ndesc: {r['description']}\nentry: {r['bash_entry']}\n")
        print(body)


def build_index(rev=None):
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(str(DB))
    con.executescript(SCHEMA.read_text())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for cid, title, desc in CATEGORIES:
        con.execute("INSERT INTO categories(id,title,description) VALUES (?,?,?)", (cid, title, desc))
    for tid, name, cat, bash_entry, py_impl, desc, tags in SEEDS:
        con.execute(
            "INSERT INTO tools(id,name,category,bash_entry,python_impl,description,tags,version,created_by,created_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?)",
            (tid, name, cat, bash_entry, py_impl, desc, tags, "0.1.0", "t1-rehome", now),
        )
    if rev is None:
        rev = "1"
    con.execute("INSERT INTO toolbox_meta(k,v) VALUES ('rev',?)", (str(rev),))
    con.execute("INSERT INTO toolbox_meta(k,v) VALUES ('updated_at',?)", (now,))
    con.execute("INSERT INTO toolbox_meta(k,v) VALUES ('schema_version',?)", ("0.1",))
    con.commit()
    tools = [
        {"id": t[0], "name": t[1], "category": t[2], "bash_entry": t[3],
         "python_impl": t[4], "description": t[5], "tags": t[6]}
        for t in SEEDS
    ]
    INDEX_JSON.write_text(json.dumps({"rev": str(rev), "updated_at": now, "tools": tools}, indent=2))
    con.close()
    print(f"built {DB} + {INDEX_JSON} rev={rev} tools={len(tools)}")


def cmd_sync(args):
    if args.check:
        if not DB.exists() or not INDEX_JSON.exists():
            print("STALE: missing index.sqlite3 or index.json")
            raise SystemExit(2)
        con = sqlite3.connect(str(DB))
        try:
            db_rev = con.execute("SELECT v FROM toolbox_meta WHERE k='rev'").fetchone()[0]
            n_tools = con.execute("SELECT COUNT(*) FROM tools WHERE deprecated_by IS NULL").fetchone()[0]
        except Exception:  # noqa: BLE001
            print("STALE: toolbox_meta.rev missing")
            raise SystemExit(2)
        finally:
            con.close()
        try:
            file_rev = json.loads(INDEX_JSON.read_text())["rev"]
        except Exception:  # noqa: BLE001
            print("STALE: index.json unreadable")
            raise SystemExit(2)
        if str(db_rev) != str(file_rev):
            print(f"STALE: db rev={db_rev} != index.json rev={file_rev}")
            raise SystemExit(2)
        print(f"fresh: rev={db_rev} tools={n_tools}")
        return
    old_rev = None
    if DB.exists():
        try:
            con = sqlite3.connect(str(DB))
            con.row_factory = sqlite3.Row
            old_rev = con.execute("SELECT v FROM toolbox_meta WHERE k='rev'").fetchone()[0]
            rev = args.rev or (str(int(old_rev) + 1) if old_rev and str(old_rev).isdigit() else "1")
            n = rebuild_index_json(con, rev)
            con.commit()
            con.close()
            print(f"synced {DB} + {INDEX_JSON} rev={rev} tools={n}")
            return
        except SystemExit:
            raise
        except Exception:  # noqa: BLE001
            old_rev = None
    rev = args.rev or (str(int(old_rev) + 1) if old_rev and str(old_rev).isdigit() else "1")
    build_index(rev=rev)


def meter_run(tool_id, ok, ms, session="default", note=""):
    con = sqlite3.connect(str(DB))
    try:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        con.execute(
            "INSERT INTO usage_log(ts, tool_id, session, ok, ms, note) VALUES (?,?,?,?,?,?)",
            (ts, tool_id, session, 1 if ok else 0, int(ms), note),
        )
        con.execute(
            "UPDATE tools SET uses = uses + 1, successes = successes + ? WHERE id=?",
            (1 if ok else 0, tool_id),
        )
        con.commit()
    finally:
        con.close()


def cmd_stats(args):
    con = db_connect()
    tier = getattr(args, "tier", 0) or 0
    tier_filter_ids(tier)  # fail-closed on bad tier
    if args.category:
        rows = con.execute(
            "SELECT * FROM tools WHERE category=? AND deprecated_by IS NULL ORDER BY uses DESC, id",
            (args.category,),
        ).fetchall()
    else:
        rows = con.execute(
            "SELECT * FROM tools WHERE deprecated_by IS NULL ORDER BY uses DESC, id"
        ).fetchall()
    rows = apply_tier(rows, tier)
    try:
        total = con.execute("SELECT COUNT(*) FROM usage_log").fetchone()[0]
        oks = con.execute("SELECT COUNT(*) FROM usage_log WHERE ok=1").fetchone()[0]
        avg = con.execute("SELECT AVG(ms) FROM usage_log").fetchone()[0]
    except Exception:  # noqa: BLE001
        total, oks, avg = 0, 0, 0
    con.close()
    tools = []
    for r in rows[: args.top]:
        d = dict(r)
        uses = d.get("uses") or 0
        succ = d.get("successes") or 0
        d["success_rate"] = round(succ / uses, 3) if uses else 0.0
        tools.append(d)
    totals = {"runs": total, "successes": oks, "avg_ms": round(avg or 0, 1)}
    if args.format == "json":
        print(json.dumps({"ok": True, "data": {"tools": tools, "totals": totals}}, indent=2))
    else:
        for t in tools:
            print(
                f"{t['id']} [{t['category']}] uses={t['uses']} "
                f"successes={t['successes']} rate={t['success_rate']:.0%}"
            )
        print(f"totals: runs={total} successes={oks} avg_ms={totals['avg_ms']}")


def cmd_lint(args):
    con = db_connect()
    rows = con.execute("SELECT * FROM tools WHERE deprecated_by IS NULL").fetchall()
    con.close()
    errors = []
    for r in rows:
        tid = r["id"]
        bash_entry = ROOT / r["bash_entry"]
        py_impl = ROOT / r["python_impl"]
        tool_md = ROOT / r["bash_entry"].replace("/run.sh", "/TOOL.md")
        if not bash_entry.exists():
            errors.append(f"{tid}: missing {r['bash_entry']}")
        else:
            try:
                head = bash_entry.read_text().splitlines()
                if not any("set -euo pipefail" in ln for ln in head):
                    errors.append(f"{tid}: run.sh missing set -euo pipefail")
                if not any("uv run python" in ln or "uv run  python" in ln for ln in head):
                    errors.append(f"{tid}: run.sh missing uv run python")
            except Exception as e:  # noqa: BLE001
                errors.append(f"{tid}: run.sh unreadable: {e}")
        if not py_impl.exists():
            errors.append(f"{tid}: missing {r['python_impl']}")
        if not tool_md.exists():
            errors.append(f"{tid}: missing TOOL.md")
        else:
            try:
                lines = tool_md.read_text().splitlines()
                if len(lines) > 15:
                    errors.append(f"{tid}: TOOL.md {len(lines)} lines > 15")
                body = "\n".join(lines).lower()
                for key in ("purpose", "usage", "limits"):
                    if key not in body:
                        errors.append(f"{tid}: TOOL.md missing {key}")
            except Exception as e:  # noqa: BLE001
                errors.append(f"{tid}: TOOL.md unreadable: {e}")
    if args.format == "json":
        print(json.dumps({"ok": not errors, "data": {"tools": len(rows), "errors": errors}}, indent=2))
    else:
        if errors:
            for e in errors:
                print(f"ERR {e}")
        print(f"lint: {len(rows)} tools, {len(errors)} errors")
    if errors:
        raise SystemExit(1)


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")
    return s or "tool"


def derive_id(category, title, explicit=""):
    if explicit:
        return explicit.strip()
    t = title.strip()
    if "." in t and re.match(r"^[a-z0-9_]+\.[a-z0-9_]+$", t):
        return t
    return f"{category}.{slugify(t)}"


def proposals_dir():
    d = ROOT / ".sandbox" / "toolbox_proposals"
    d.mkdir(parents=True, exist_ok=True)
    return d


def ledger_append(record):
    ledger = ROOT / ".meta" / ".omt" / "ledger.jsonl"
    try:
        rec = {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
        rec.update(record)
        with ledger.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
    except Exception as e:  # noqa: BLE001
        print(f"ledger append failed: {e}", file=sys.stderr)


def rebuild_index_json(con, rev):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = con.execute(
        "SELECT id,name,category,bash_entry,python_impl,description,tags "
        "FROM tools WHERE deprecated_by IS NULL ORDER BY id"
    ).fetchall()
    tools = [
        {"id": r["id"], "name": r["name"], "category": r["category"],
         "bash_entry": r["bash_entry"], "python_impl": r["python_impl"],
         "description": r["description"], "tags": r["tags"]}
        for r in rows
    ]
    con.execute("UPDATE toolbox_meta SET v=? WHERE k='rev'", (str(rev),))
    con.execute("UPDATE toolbox_meta SET v=? WHERE k='updated_at'", (now,))
    INDEX_JSON.write_text(json.dumps({"rev": str(rev), "updated_at": now, "tools": tools}, indent=2))
    return len(tools)


def bump_rev(con):
    row = con.execute("SELECT v FROM toolbox_meta WHERE k='rev'").fetchone()
    old = row[0] if row else "1"
    rev = str(int(old) + 1) if str(old).isdigit() else "2"
    return rev


def cmd_propose(args):
    cats = {c[0] for c in CATEGORIES}
    if args.category not in cats:
        print(json.dumps({"ok": False, "error": f"unknown category {args.category}"}))
        raise SystemExit(1)
    tid = derive_id(args.category, args.title, args.id)
    if "." not in tid or tid.count(".") != 1:
        print(json.dumps({"ok": False, "error": f"bad tool id {tid} (want <category>.<name>)"}))
        raise SystemExit(1)
    con = db_connect()
    try:
        if con.execute("SELECT 1 FROM tools WHERE id=?", (tid,)).fetchone():
            print(json.dumps({"ok": False, "error": f"tool {tid} already indexed"}))
            raise SystemExit(1)
        if con.execute("SELECT 1 FROM proposals WHERE id=?", (tid,)).fetchone():
            print(json.dumps({"ok": False, "error": f"proposal {tid} already staged"}))
            raise SystemExit(1)
        motive = args.motive.strip()
        if args.general_use and "[general-use]" not in motive:
            motive = motive + " [general-use]"
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        draft_name = tid.replace(".", "_") + ".md"
        draft_path = f".sandbox/toolbox_proposals/{draft_name}"
        (proposals_dir() / draft_name).write_text(
            f"# Proposal {tid}\n- title: {args.title}\n- category: {args.category}\n"
            f"- motive: {motive}\n- uses_seen: {args.uses_seen}\n"
            f"{'[general-use] ' if args.general_use else ''}created: {now}\n"
            "- evidence: (1) motive cites recurring use; (2) uses_seen count in DB\n"
            "- contract: `<cat>/<name>/run.sh` (set -euo pipefail, uv-only) + `main.py` (argparse, JSON) + `TOOL.md` (<=15 lines: purpose/usage/args/I-O/limits)\n"
            "- denies: no push/fetch/clone, no bare python/pip/pytest, no *.env reads, no network\n"
        )
        con.execute(
            "INSERT INTO proposals(id,title,category,motive,status,draft_path,uses_seen,created_at)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (tid, args.title, args.category, motive, "staged", draft_path, args.uses_seen, now),
        )
        con.commit()
    finally:
        con.close()
    if args.format == "json":
        print(json.dumps({"ok": True, "data": {"id": tid, "status": "staged", "draft": draft_path}}, indent=2))
    else:
        print(f"proposed {tid} [staged] draft={draft_path}")


def cmd_approve(args):
    con = db_connect()
    try:
        r = con.execute("SELECT * FROM proposals WHERE id=?", (args.tool_id,)).fetchone()
        if not r:
            print(json.dumps({"ok": False, "error": f"unknown proposal {args.tool_id}"}))
            raise SystemExit(1)
        if r["status"] != "staged":
            print(json.dumps({"ok": False, "error": f"proposal {args.tool_id} is {r['status']}, not staged"}))
            raise SystemExit(1)
        con.execute("UPDATE proposals SET status='approved' WHERE id=?", (args.tool_id,))
        con.commit()
    finally:
        con.close()
    if args.format == "json":
        print(json.dumps({"ok": True, "data": {"id": args.tool_id, "status": "approved"}}))
    else:
        print(f"approved {args.tool_id}")


def cmd_reject(args):
    con = db_connect()
    try:
        r = con.execute("SELECT * FROM proposals WHERE id=?", (args.tool_id,)).fetchone()
        if not r:
            print(json.dumps({"ok": False, "error": f"unknown proposal {args.tool_id}"}))
            raise SystemExit(1)
        if r["status"] not in ("staged", "approved"):
            print(json.dumps({"ok": False, "error": f"proposal {args.tool_id} already {r['status']}"}))
            raise SystemExit(1)
        con.execute("UPDATE proposals SET status='rejected' WHERE id=?", (args.tool_id,))
        con.commit()
        n_tools = con.execute("SELECT COUNT(*) FROM tools").fetchone()[0]
        db_rev = con.execute("SELECT v FROM toolbox_meta WHERE k='rev'").fetchone()[0]
    finally:
        con.close()
    # reject leaves index untouched: tools + rev unchanged by construction
    if args.format == "json":
        print(json.dumps({"ok": True, "data": {"id": args.tool_id, "status": "rejected",
                                               "tools": n_tools, "rev": db_rev}}))
    else:
        print(f"rejected {args.tool_id} (index untouched: tools={n_tools} rev={db_rev})")


def cmd_proposals(args):
    con = db_connect()
    if args.status:
        rows = con.execute("SELECT * FROM proposals WHERE status=? ORDER BY id", (args.status,)).fetchall()
    else:
        rows = con.execute("SELECT * FROM proposals ORDER BY status, id").fetchall()
    con.close()
    if args.format == "json":
        print(json.dumps({"ok": True, "data": [dict(r) for r in rows]}, indent=2))
    else:
        for r in rows:
            print(f"{r['id']} [{r['status']}] uses_seen={r['uses_seen']} — {r['title']}")


PILOT_IMPL = {
    "git.recent_log": '''"""git.recent_log — rehomed `git log` recipe (T3 pilot, no new logic class)."""
import argparse
import json
import subprocess


def main():
    ap = argparse.ArgumentParser(description="recent git log oneline")
    ap.add_argument("--lines", type=int, default=10)
    args = ap.parse_args()
    try:
        out = subprocess.run(
            ["git", "log", "--oneline", f"-{max(1, args.lines)}"],
            capture_output=True, text=True, timeout=15,
        )
        print(json.dumps({"ok": out.returncode == 0,
                           "data": {"log": out.stdout.strip(), "rc": out.returncode}}))
        raise SystemExit(out.returncode)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
''',
}

GENERIC_IMPL = '''"""{tid} — promoted via toolbox promote (T3 gated growth)."""
import argparse
import json


def main():
    ap = argparse.ArgumentParser(description="{title}")
    ap.add_argument("--lines", type=int, default=5)
    args = ap.parse_args()
    print(json.dumps({{"ok": True, "data": {{"tool": "{tid}", "lines": args.lines}}}}))


if __name__ == "__main__":
    main()
'''


def cmd_promote(args):
    con = db_connect()
    try:
        p = con.execute("SELECT * FROM proposals WHERE id=?", (args.tool_id,)).fetchone()
        if not p:
            print(json.dumps({"ok": False, "error": f"unknown proposal {args.tool_id}"}))
            raise SystemExit(1)
        if p["status"] != "approved":
            print(json.dumps({"ok": False, "error": f"proposal {args.tool_id} is {p['status']} — approve first (mandatory gate)"}))
            raise SystemExit(1)
        motive = p["motive"] or ""
        general = "[general-use]" in motive
        if general and (p["uses_seen"] or 0) < 1:
            print(json.dumps({"ok": False, "error": "need >=1 observed use + general-use tag"}))
            raise SystemExit(1)
        if not general and (p["uses_seen"] or 0) < 2:
            print(json.dumps({"ok": False, "error": f"need >=2 observed uses (seen={p['uses_seen']}) or general-use tag"}))
            raise SystemExit(1)
        if con.execute("SELECT 1 FROM tools WHERE id=?", (args.tool_id,)).fetchone():
            print(json.dumps({"ok": False, "error": f"tool {args.tool_id} already indexed"}))
            raise SystemExit(1)
        cat, name = args.tool_id.split(".", 1)
        if cat != p["category"]:
            print(json.dumps({"ok": False, "error": f"id category {cat} != proposal {p['category']}"}))
            raise SystemExit(1)
        tdir = ROOT / "toolbox" / cat / name
        if tdir.exists():
            print(json.dumps({"ok": False, "error": f"dir {tdir} already exists"}))
            raise SystemExit(1)
        tdir.mkdir(parents=True)
        (tdir / "run.sh").write_text(
            "#!/usr/bin/env bash\nset -euo pipefail\n"
            'HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"\n'
            'exec uv run python "$HERE/main.py" "$@"\n'
        )
        (tdir / "run.sh").chmod(0o755)
        impl = PILOT_IMPL.get(args.tool_id, GENERIC_IMPL.format(tid=args.tool_id, title=p["title"]))
        (tdir / "main.py").write_text(impl)
        (tdir / "TOOL.md").write_text(
            f"# {args.tool_id}\n- purpose: {p['title']} (promoted: {p['motive'][:80]}).\n"
            f"- usage: `uv run scripts/toolbox/toolbox.py run {args.tool_id}`\n"
            "- args: --lines N (default 10 for log; 5 generic).\n"
            "- I/O: stdout JSON `{\"ok\":…, \"data\":…}`.\n"
            "- example: query then run without forking ad-hoc bash.\n"
            "- limits: read-only; uv-only; no push/fetch/clone; no *.env reads.\n"
        )
        bash_entry = f"toolbox/{cat}/{name}/run.sh"
        py_impl = f"toolbox/{cat}/{name}/main.py"
        tags = f"{cat},{name},promoted"
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        con.execute(
            "INSERT INTO tools(id,name,category,bash_entry,python_impl,description,tags,version,created_by,created_at,promoted_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (args.tool_id, name, cat, bash_entry, py_impl, p["title"], tags,
             "0.1.0", "toolbox-promote", now, now),
        )
        test_path = ROOT / "tests" / "scripts" / "toolbox" / f"test_{name}.py"
        test_path.write_text(
            f'"""Promoted tool {args.tool_id} — scaffold test (T3 gate)."""\n'
            "import json\nimport subprocess\nimport sys\nfrom pathlib import Path\n\n"
            "ROOT = Path(__file__).resolve().parents[3]\n"
            'CLI = [sys.executable, str(ROOT / "scripts" / "toolbox" / "toolbox.py")]\n\n\n'
            f"def test_promoted_{name}_runs():\n"
            f'    out = subprocess.run([*CLI, "run", "{args.tool_id}"], capture_output=True, text=True, timeout=60)\n'
            "    assert out.returncode == 0, out.stderr + out.stdout\n"
            '    assert "ok" in out.stdout.lower()\n\n\n'
            f"def test_promoted_{name}_queryable():\n"
            f'    out = subprocess.run([*CLI, "query", "{name}", "--format", "json"], capture_output=True, text=True, timeout=30)\n'
            "    assert out.returncode == 0, out.stderr\n"
            f'    ids = [r["id"] for r in json.loads(out.stdout)["data"]]\n'
            f'    assert "{args.tool_id}" in ids\n'
        )
        rev = bump_rev(con)
        n = rebuild_index_json(con, rev)
        con.execute("UPDATE proposals SET status='promoted' WHERE id=?", (args.tool_id,))
        con.commit()
    finally:
        con.close()
    ledger_append({"kind": "toolbox_promote", "tool": args.tool_id, "rev": rev})
    if args.format == "json":
        print(json.dumps({"ok": True, "data": {"id": args.tool_id, "rev": rev, "tools": n}}, indent=2))
    else:
        print(f"promoted {args.tool_id} rev={rev} tools={n}")


def cmd_prune(args):
    con = db_connect()
    try:
        days = args.stale_days
        cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
        rows = con.execute("SELECT * FROM tools WHERE deprecated_by IS NULL").fetchall()
        cands = []
        for r in rows:
            try:
                created = datetime.strptime(r["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=timezone.utc).timestamp()
            except Exception:  # noqa: BLE001
                created = 0
            if (r["uses"] or 0) == 0 and created < cutoff:
                cands.append(r["id"])
        depr = [r["id"] for r in con.execute(
            "SELECT id FROM tools WHERE deprecated_by IS NOT NULL").fetchall()]
        action = "list"
        if args.deprecate:
            tid = args.deprecate
            r = con.execute("SELECT * FROM tools WHERE id=?", (tid,)).fetchone()
            if not r:
                print(json.dumps({"ok": False, "error": f"unknown tool {tid}"}))
                raise SystemExit(1)
            if r["deprecated_by"]:
                print(json.dumps({"ok": False, "error": f"{tid} already deprecated"}))
                raise SystemExit(1)
            by = args.by or "prune:unused"
            con.execute("UPDATE tools SET deprecated_by=? WHERE id=?", (by, tid))
            rev = bump_rev(con)
            rebuild_index_json(con, rev)
            con.commit()
            ledger_append({"kind": "toolbox_prune", "tool": tid, "action": "deprecate", "by": by})
            action = f"deprecated {tid} by {by} rev={rev}"
        elif args.remove:
            tid = args.remove
            r = con.execute("SELECT * FROM tools WHERE id=?", (tid,)).fetchone()
            if not r:
                print(json.dumps({"ok": False, "error": f"unknown tool {tid}"}))
                raise SystemExit(1)
            if not r["deprecated_by"]:
                print(json.dumps({"ok": False, "error": f"{tid} not deprecated — deprecate first (one-cycle warning)"}))
                raise SystemExit(1)
            tdir = ROOT / r["bash_entry"].replace("/run.sh", "")
            con.execute("DELETE FROM tools WHERE id=?", (tid,))
            rev = bump_rev(con)
            rebuild_index_json(con, rev)
            con.commit()
            if tdir.exists():
                shutil.rmtree(tdir)
            tpath = ROOT / "tests" / "scripts" / "toolbox" / f"test_{r['name']}.py"
            if tpath.exists():
                tpath.unlink()
            ledger_append({"kind": "toolbox_prune", "tool": tid, "action": "remove"})
            action = f"removed {tid} rev={rev}"
    finally:
        con.close()
    if args.format == "json":
        print(json.dumps({"ok": True, "data": {"candidates": cands, "deprecated": depr,
                                               "action": action}}, indent=2))
    else:
        print(f"prune candidates (uses==0, >{days}d): {cands or 'none'}")
        if depr:
            print(f"deprecated: {depr}")
        if action != "list":
            print(action)


def cmd_tiers(args):
    con = db_connect()
    rows = con.execute("SELECT * FROM tools WHERE deprecated_by IS NULL ORDER BY id").fetchall()
    con.close()
    full = [dict(r) for r in rows]
    core = [t for t in full if t["id"] in set(TIER1_CORE)]
    # T1 core-5 must stay exact: warn (not fail) if a seed is deprecated/missing
    data = {
        "tier1": {"desc": "core-5 rehomed seeds (harnessc Tier-1 payload)", "tools": [t["id"] for t in core]},
        "tier2": {"desc": "full set (Tier-1 + promoted)", "tools": [t["id"] for t in full]},
        "tier3": {"desc": "full set (receipt/MVC live in harness, not toolbox)", "tools": [t["id"] for t in full]},
    }
    if args.format == "json":
        print(json.dumps({"ok": True, "data": data}, indent=2))
    else:
        print(f"tier1 core-5: {data['tier1']['tools']}")
        print(f"tier2 full ({len(full)}): {data['tier2']['tools']}")
        print(f"tier3 full ({len(full)}): {data['tier3']['tools']}")


def build_docs_content():
    """Render T4 generated docs from the live DB (pure vs files, no writes).

    Returns (rev, n_tools, files) where files maps repo-rel path -> text.
    Categories/tools lists exclude deprecated_by (tiers/prune discipline).
    """
    con = db_connect()
    try:
        cats = con.execute("SELECT * FROM categories ORDER BY id").fetchall()
        tools = con.execute(
            "SELECT * FROM tools WHERE deprecated_by IS NULL ORDER BY category, id"
        ).fetchall()
        rev = con.execute("SELECT v FROM toolbox_meta WHERE k='rev'").fetchone()[0]
    finally:
        con.close()
    cats = [dict(c) for c in cats]
    tools = [dict(t) for t in tools]
    per_cat = {}
    for t in tools:
        per_cat.setdefault(t["category"], []).append(t)
    lines = [
        "# toolbox/categories — taxonomy (GENERATED by `toolbox.py docs --gen`, do not hand-edit)",
        "",
        f"> rev={rev} tools={len(tools)} categories={len(cats)}",
        "> Tier-1: core-5 rehomed seeds. Tier-2/3: full set (incl. promoted).",
        "",
        "| category | title | tools | ids |",
        "|---|---|---|---|",
    ]
    for c in cats:
        ids = [t["id"] for t in per_cat.get(c["id"], [])]
        lines.append(f"| {c['id']} | {c['title']} | {len(ids)} | {', '.join(ids) or '—'} |")
    lines += ["", "## Tier map", "- tier1: " + ", ".join(TIER1_CORE),
              "- tier2/3: full non-deprecated set (see `toolbox.py tiers`)", ""]
    categories_md = "\n".join(lines)
    tl = [
        "# toolbox/tools — per-tool docs index (GENERATED by `toolbox.py docs --gen`)",
        "",
        f"> rev={rev} tools={len(tools)} — contract: `<cat>/<name>/run.sh` (set -euo pipefail, uv-only) + `main.py` (JSON) + `TOOL.md` (<=15).",
        "",
    ]
    for t in tools:
        tl += [
            f"## {t['id']}",
            f"- category: {t['category']} — {t['description']}",
            f"- run: `uv run scripts/toolbox/toolbox.py run {t['id']}`",
            f"- entry: `{t['bash_entry']}` tags: `{t['tags']}` uses={t['uses']} successes={t['successes']}",
            "",
        ]
    tools_md = "\n".join(tl)
    snippet = f"toolbox: {len(tools)} tools rev={rev} - query: toolbox.py query \"...\""
    onboarding = "\n".join([
        "# toolbox onboarding (GENERATED snippet)",
        "",
        snippet,
        "",
        "## Discover in <=2 calls",
        "1. `uv run scripts/toolbox/toolbox.py query \"<keywords>\"` (add `--tier 1` for core-5 only)",
        "2. `uv run scripts/toolbox/toolbox.py show <id>` then `run <id> -- --help`",
        "",
        "## Tiers",
        "- Tier-1 (minimal): core-5 rehomed seeds — git.status_summary, ledger.window_slice,",
        "  harness.budget_check, text.json_split, session.pause_note_append.",
        "- Tier-2/3 (full): all non-deprecated tools incl. promoted (see `tiers`).",
        "",
        "## Grow / prune",
        "- encounter 2x (or 1x general-use) -> `propose` (staged) -> approve -> `promote` -> `run` metered.",
        "- `stats` shows uses/successes; `prune` deprecates uses==0 >90d (one-cycle warning).",
        "",
        f"> rev={rev} tools={len(tools)} categories={len(cats)} — regen: `toolbox.py docs --gen`, check: `docs --check`.",
        "",
    ])
    files = {
        "toolbox/categories.md": categories_md + "\n",
        "toolbox/tools.md": tools_md,
        "toolbox/STARTUP_SNIPPET.txt": snippet + "\n",
        "toolbox/ONBOARDING.md": onboarding,
    }
    return str(rev), len(tools), files


def cmd_docs(args):
    if not (args.gen or args.check):
        print("docs: pass --gen to regenerate or --check to verify freshness", file=sys.stderr)
        raise SystemExit(2)
    rev, n, files = build_docs_content()
    if args.check:
        stale = []
        for rel, want in files.items():
            p = ROOT / rel
            if not p.exists() or p.read_text() != want:
                stale.append(rel)
        if stale:
            print(f"STALE docs rev={rev} tools={n}: {', '.join(stale)} — run `toolbox.py docs --gen`")
            raise SystemExit(2)
        print(f"fresh docs rev={rev} tools={n} files={len(files)}")
        return
    for rel, text in files.items():
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    snippet_bytes = len(files["toolbox/STARTUP_SNIPPET.txt"].strip().encode())
    print(f"docs rev={rev} tools={n} files={len(files)} snippet={snippet_bytes}B")
    if snippet_bytes > 120:
        print(f"ERR startup snippet {snippet_bytes}B > 120B budget", file=sys.stderr)
        raise SystemExit(1)


def cmd_run(args):
    # T2 metered run (usage_log + uses/successes).
    con = db_connect()
    r = con.execute("SELECT * FROM tools WHERE id=?", (args.tool_id,)).fetchone()
    con.close()
    if not r:
        print(json.dumps({"ok": False, "error": f"unknown tool {args.tool_id}"}))
        raise SystemExit(1)
    entry = ROOT / r["bash_entry"]
    session = os.environ.get("TOOLBOX_SESSION", "default")
    note = os.environ.get("TOOLBOX_NOTE", "")
    start = time.monotonic()
    out = subprocess.run(["bash", str(entry), *args.tool_args], capture_output=True, text=True, timeout=120)
    ms = (time.monotonic() - start) * 1000
    ok = out.returncode == 0
    try:
        meter_run(args.tool_id, ok, ms, session=session, note=note)
    except Exception as e:  # noqa: BLE001
        print(f"metering failed: {e}", file=sys.stderr)
    sys.stdout.write(out.stdout)
    sys.stderr.write(out.stderr)
    raise SystemExit(out.returncode)


def main():
    ap = argparse.ArgumentParser(prog="toolbox.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("query")
    q.add_argument("keywords", nargs="?", default="")
    q.add_argument("--limit", type=int, default=5)
    q.add_argument("--format", default="text", choices=["text", "json"])
    q.add_argument("--tier", type=int, default=0, help="1=core-5 only, 2/3=full set")
    q.set_defaults(fn=cmd_query)
    li = sub.add_parser("list")
    li.add_argument("--category", default="")
    li.add_argument("--format", default="text", choices=["text", "json"])
    li.add_argument("--tier", type=int, default=0, help="1=core-5 only, 2/3=full set")
    li.set_defaults(fn=cmd_list)
    sh = sub.add_parser("show")
    sh.add_argument("tool_id")
    sh.add_argument("--format", default="text", choices=["text", "json"])
    sh.set_defaults(fn=cmd_show)
    sy = sub.add_parser("sync")
    sy.add_argument("--check", action="store_true")
    sy.add_argument("--rev", default="")
    sy.set_defaults(fn=cmd_sync)
    rn = sub.add_parser("run")
    rn.add_argument("tool_id")
    rn.add_argument("tool_args", nargs=argparse.REMAINDER)
    rn.set_defaults(fn=cmd_run)
    st = sub.add_parser("stats")
    st.add_argument("--top", type=int, default=10)
    st.add_argument("--category", default="")
    st.add_argument("--format", default="text", choices=["text", "json"])
    st.add_argument("--tier", type=int, default=0, help="1=core-5 only, 2/3=full set")
    st.set_defaults(fn=cmd_stats)
    li2 = sub.add_parser("lint")
    li2.add_argument("--format", default="text", choices=["text", "json"])
    li2.set_defaults(fn=cmd_lint)
    pr = sub.add_parser("propose")
    pr.add_argument("--title", required=True)
    pr.add_argument("--category", required=True)
    pr.add_argument("--motive", required=True)
    pr.add_argument("--draft", default="")
    pr.add_argument("--id", default="")
    pr.add_argument("--uses-seen", type=int, default=1)
    pr.add_argument("--general-use", action="store_true")
    pr.add_argument("--format", default="text", choices=["text", "json"])
    pr.set_defaults(fn=cmd_propose)
    av = sub.add_parser("approve")
    av.add_argument("tool_id")
    av.add_argument("--format", default="text", choices=["text", "json"])
    av.set_defaults(fn=cmd_approve)
    rj = sub.add_parser("reject")
    rj.add_argument("tool_id")
    rj.add_argument("--format", default="text", choices=["text", "json"])
    rj.set_defaults(fn=cmd_reject)
    pm = sub.add_parser("promote")
    pm.add_argument("tool_id")
    pm.add_argument("--format", default="text", choices=["text", "json"])
    pm.set_defaults(fn=cmd_promote)
    pn = sub.add_parser("prune")
    pn.add_argument("--deprecate", default="")
    pn.add_argument("--remove", default="")
    pn.add_argument("--by", default="")
    pn.add_argument("--stale-days", type=int, default=90)
    pn.add_argument("--format", default="text", choices=["text", "json"])
    pn.set_defaults(fn=cmd_prune)
    ps = sub.add_parser("proposals")
    ps.add_argument("--status", default="")
    ps.add_argument("--format", default="text", choices=["text", "json"])
    ps.set_defaults(fn=cmd_proposals)
    tr = sub.add_parser("tiers")
    tr.add_argument("--format", default="text", choices=["text", "json"])
    tr.set_defaults(fn=cmd_tiers)
    dc = sub.add_parser("docs")
    dc.add_argument("--gen", action="store_true", help="regenerate categories.md/tools.md/snippets")
    dc.add_argument("--check", action="store_true", help="verify generated docs are fresh")
    dc.set_defaults(fn=cmd_docs)
    args = ap.parse_args()
    if args.cmd == "run" and args.tool_args and args.tool_args[0] == "--":
        args.tool_args = args.tool_args[1:]
    args.fn(args)


if __name__ == "__main__":
    main()
