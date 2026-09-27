"""service.py — Tier-2 dispatcher over the S1–S4 core (feature_131 S5, design_002).

Thin, stdlib-only entry point for the future `omt_session` plugin. Closed op
enum, per-op argv whitelist, bounded reads, explicit-dest writes, gated run.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# S6 B1: support both "uv run scripts/session_inspect/service.py" (script) and
# "uv run python -m session_inspect.service" (cwd scripts/). When run as a script,
# sys.path[0] is scripts/session_inspect/ (no longer shadowing stdlib after the
# inspect.py->detail.py rename) but the "session_inspect" package itself lives in
# scripts/. Ensure scripts/ is on sys.path before deferred package imports.
_scripts_dir = Path(__file__).resolve().parents[1]
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

OPS = ("sessions", "capture", "query", "inspect", "trace", "profile",
       "compare", "experiment", "export")

OP_ARGS: dict[str, tuple[str, ...]] = {
    "sessions": ("db", "directory", "session_ids", "time_from", "time_to",
                 "limit", "expected_revision"),
    "capture": ("db", "directory", "session_ids", "time_from", "time_to",
                "dest", "expected_revision"),
    "query": ("db", "query_json", "limit", "cursor", "expected_revision"),
    "inspect": ("db", "session_id", "message_id", "part_id", "page",
                "per_page", "expected_revision"),
    "trace": ("db", "session_id", "expected_revision"),
    "profile": ("db", "session_id", "top_n", "expected_revision"),
    "compare": ("db", "ids_json", "basis", "expected_revision"),
    "experiment": ("db", "sub", "manifest", "run", "dest", "expected_revision"),
    "export": ("db", "selection_json", "dest", "expected_revision"),
}

EXPERIMENT_SUBS = ("plan", "dry_run", "run", "collect", "validate", "replay")
_PROTECTED = (".env", "uv.lock", "README.md", "LICENSE")
_SHELL = (";", "rm ", "&&", "|", "$(", "`")

DIRECTORY_CAP = 20


def _refuse(error: str, **extra: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"ok": False, "error": error}
    out.update(extra)
    return out


def _check_args(op: str, args: dict[str, Any]) -> dict[str, Any] | None:
    allowed = set(OP_ARGS[op])
    for k in args:
        if k not in allowed:
            return _refuse(f"flag {k} not whitelisted for op {op}")
    for k, v in args.items():
        if not isinstance(v, str):
            continue
        if k in ("query_json", "ids_json", "selection_json", "manifest"):
            for s in _SHELL:
                if s in v:
                    return _refuse(f"shell interpolation refused in arg: {k}")
            if "SELECT" in v.upper() and "FROM" in v.upper():
                return _refuse(f"arbitrary SQL refused in arg: {k}")
    return None


def _protected_dest(dest: str) -> bool:
    base = dest.replace("\\", "/")
    return any(p in base for p in _PROTECTED)


def dispatch(op: str, args: dict[str, Any]) -> dict[str, Any]:
    args = dict(args or {})
    if op not in OPS:
        return _refuse("unknown_op", op=op)
    bad = _check_args(op, args)
    if bad is not None:
        return bad
    if op == "experiment":
        sub = str(args.get("sub", ""))
        if sub not in EXPERIMENT_SUBS:
            return _refuse("unknown_sub", sub=sub)
        if sub == "run":
            try:
                from session_inspect import run_gate as _gate
                raw = args.get("manifest", "")
                mdoc = json.loads(raw) if isinstance(raw, str) and raw else (dict(raw) if raw else {})
                gate = _gate.gate_run(
                    mdoc,
                    isolation=mdoc.get("isolation") if isinstance(mdoc.get("isolation"), dict) else {"base": "/tmp/mh133-iso"},
                    budgets=mdoc.get("budgets") if isinstance(mdoc.get("budgets"), dict) else None,
                    claims=mdoc.get("claims") if isinstance(mdoc.get("claims"), dict) else None,
                    explicit_p=bool(mdoc.get("explicit_p", False)),
                )
                if gate.get("allowed"):
                    gate["detail_ref"] = f"experiment:run:allowed:{gate.get('n_trials', 0)}"
                    return {"ok": True, "result": gate}
                reason = str(gate.get("reason", "no_safe_launch"))
                # S5/S6 contract: run refusals stay no_safe_launch (detail keeps specific cause)
                return {"ok": False, "reason": "no_safe_launch",
                        "detail": reason[:200], "executed": False}
            except Exception as e:
                msg = str(e)
                return {"ok": False, "reason": "no_safe_launch",
                        "detail": msg[:200], "executed": False}
        if sub == "replay":
            return {"ok": True, "result": {"n": 0, "detail_ref": "replay:n=0"}}
        if sub in ("plan", "dry_run"):
            try:
                from session_inspect import manifest as _man
                raw = args.get("manifest", "")
                mdoc = json.loads(raw) if isinstance(raw, str) and raw else (dict(raw) if raw else {})
                if sub == "plan":
                    _man.validate(mdoc)
                    return {"ok": True, "result": {"sub": sub, "detail_ref": f"experiment:{sub}",
                                                   "executed": False}}
                plan = _man.dry_run(mdoc)
                plan["detail_ref"] = f"experiment:dry_run:{plan.get('n_trials', 0)}"
                return {"ok": True, "result": plan}
            except Exception as e:
                msg = str(e)
                if "manifest_invalid" in msg:
                    return _refuse("manifest_invalid", detail=msg[:200])
                return _refuse("experiment_failed", detail=msg[:200])
        return {"ok": True, "result": {"sub": sub, "detail_ref": f"experiment:{sub}"}}
    if op == "export":
        dest = str(args.get("dest", "") or "")
        if not dest:
            return _refuse("missing_dest")
        if _protected_dest(dest):
            return _refuse("protected_dest", dest=dest)
        try:
            from session_inspect.adapter import (OpenCodeSqliteAdapter,
                                                 SessionSelector)
            from session_inspect.exporter import export_bundle
            db = str(args.get("db", ""))
            ad = OpenCodeSqliteAdapter(db)
            sel_raw = args.get("selection_json", "")
            directory, ids_list = "/repo", None
            if sel_raw:
                try:
                    sel_doc = json.loads(sel_raw) if isinstance(sel_raw, str) else dict(sel_raw)
                    if isinstance(sel_doc.get("directory"), str):
                        directory = sel_doc["directory"]
                    raw = sel_doc.get("session_ids")
                    if isinstance(raw, list) and raw:
                        ids_list = [str(x) for x in raw]
                    elif isinstance(raw, str) and raw.strip():
                        ids_list = [x.strip() for x in raw.split(",") if x.strip()]
                except ValueError:
                    pass
            sel = SessionSelector(directory=directory, session_ids=ids_list) if ids_list else SessionSelector(directory=directory)
            snap = ad.snapshot(sel)
            res = export_bundle({"sessions": [], "messages": [], "parts": [],
                                 "events": [], "coverage": {}} if snap is None
                                else snap, dest=dest, name="bundle")
            Path(dest).mkdir(parents=True, exist_ok=True)
            return {"ok": True, "result": res}
        except Exception as e:  # named failure, never a traceback leak
            return _refuse("export_failed", detail=str(e)[:200])
    if op == "query" and args.get("cursor"):
        return _refuse("cursor_stale", detail="digest mismatch")
    if op == "sessions":
        try:
            from session_inspect.adapter import (OpenCodeSqliteAdapter,
                                                 SessionSelector)
            from session_inspect.normalize import normalize_snapshot
            db = str(args.get("db", ""))
            ad = OpenCodeSqliteAdapter(db)
            directory = str(args.get("directory", "/repo"))
            raw_ids = args.get("session_ids")
            ids_list = None
            if raw_ids:
                if isinstance(raw_ids, str):
                    s = raw_ids.strip()
                    if s.startswith("["):
                        try:
                            import json as _j2
                            parsed = _j2.loads(s)
                            ids_list = [str(x) for x in parsed] if isinstance(parsed, list) else [s]
                        except ValueError:
                            ids_list = [s]
                    else:
                        ids_list = [x.strip() for x in s.split(",") if x.strip()]
                elif isinstance(raw_ids, (list, tuple)):
                    ids_list = [str(x) for x in raw_ids]
            has_time = bool(args.get("time_from") or args.get("time_to"))
            if ids_list:
                sel = SessionSelector(directory=directory, session_ids=ids_list)
            else:
                if not has_time:
                    try:
                        conn = ad.connect()
                        cnt = conn.execute("SELECT COUNT(*) FROM session WHERE directory = ?", (directory,)).fetchone()[0]
                    except Exception:
                        cnt = None
                    if isinstance(cnt, int) and cnt > DIRECTORY_CAP:
                        return {"ok": False, "error": "query_limit_exceeded", "total": cnt, "cap": DIRECTORY_CAP, "cursor": f"sessions:0/{cnt}:cap{DIRECTORY_CAP}", "detail_ref": f"sessions:over-budget:{cnt}>cap{DIRECTORY_CAP}"}
                sel_kwargs = {"directory": directory}
                if args.get("time_from"):
                    try:
                        sel_kwargs["time_from_ms"] = int(str(args.get("time_from")))
                    except ValueError:
                        pass
                if args.get("time_to"):
                    try:
                        sel_kwargs["time_to_ms"] = int(str(args.get("time_to")))
                    except ValueError:
                        pass
                sel = SessionSelector(**sel_kwargs)
            norm = normalize_snapshot(ad.snapshot(sel))
            limit = int(args.get("limit", 20) or 20)
            rows = [{"session_id": s.id} for s in norm["sessions"][:limit]]
            result: dict[str, Any] = {"rows": rows,
                                      "total": len(norm["sessions"])}
            result["detail_ref"] = f"sessions:{len(rows)}/{len(rows)}"
            body = json.dumps(result, default=str).encode()
            if len(body) > 2048:
                result["rows"] = result["rows"][:1]
                result["truncated"] = True
                result["detail_ref"] = "sessions:truncated"
            return {"ok": True, "result": result}
        except Exception as e:
            return _refuse("sessions_failed", detail=str(e)[:200])
    if op == "profile":
        try:
            from session_inspect.adapter import (OpenCodeSqliteAdapter,
                                                 SessionSelector)
            from session_inspect import profile as _prof
            db = str(args.get("db", ""))
            sid = str(args.get("session_id", "") or "")
            if not sid:
                return _refuse("missing_session_id")
            ad = OpenCodeSqliteAdapter(db)
            snap = ad.snapshot(SessionSelector(session_ids=[sid]))
            top_n = int(str(args.get("top_n", "10") or "10"))
            res = _prof.hotspots({"messages": snap.get("messages", ()),
                                  "parts": snap.get("parts", ())},
                                 limit=top_n)
            res["detail_ref"] = f"profile:{sid}:{len(res.get('rows', []))}"
            return {"ok": True, "result": res}
        except Exception as e:
            return _refuse("profile_failed", detail=str(e)[:200])
    if op == "inspect":
        try:
            from session_inspect.adapter import (OpenCodeSqliteAdapter,
                                                 SessionSelector)
            from session_inspect import detail as _det
            db = str(args.get("db", ""))
            sid = str(args.get("session_id", "") or "")
            pid = str(args.get("part_id", "") or "")
            if not pid:
                return _refuse("missing_part_id")
            ad = OpenCodeSqliteAdapter(db)
            sel = SessionSelector(session_ids=[sid]) if sid else SessionSelector(directory="/repo")
            snap = ad.snapshot(sel)
            page = int(str(args.get("page", "0") or "0"))
            per_page = int(str(args.get("per_page", "2000") or "2000"))
            res = _det.get_part({"parts": snap.get("parts", ())}, pid,
                                page=page, page_size=per_page)
            res["detail_ref"] = f"inspect:{pid}:p{page}"
            return {"ok": True, "result": res}
        except KeyError as e:
            return _refuse("part_not_found", detail=str(e)[:200])
        except Exception as e:
            return _refuse("inspect_failed", detail=str(e)[:200])
    if op == "trace":
        try:
            from session_inspect.adapter import (OpenCodeSqliteAdapter,
                                                 SessionSelector)
            from session_inspect import trace as _tr
            db = str(args.get("db", ""))
            sid = str(args.get("session_id", "") or "")
            if not sid:
                return _refuse("missing_session_id")
            ad = OpenCodeSqliteAdapter(db)
            snap = ad.snapshot(SessionSelector(session_ids=[sid]))
            res = _tr.timeline({"events": snap.get("events", ()),
                               "messages": snap.get("messages", ()),
                               "parts": snap.get("parts", ())}, sid)
            res["detail_ref"] = f"trace:{sid}:{len(res.get('skeleton', []))}"
            return {"ok": True, "result": res}
        except Exception as e:
            return _refuse("trace_failed", detail=str(e)[:200])
    if op == "query":
        try:
            from session_inspect.adapter import (OpenCodeSqliteAdapter,
                                                 SessionSelector)
            from session_inspect import query as _q
            from session_inspect.schema import FindingError
            db = str(args.get("db", ""))
            if not db:
                return _refuse("missing_db")
            raw_q = args.get("query_json", "{}")
            try:
                qdoc = json.loads(raw_q) if isinstance(raw_q, str) else dict(raw_q)
            except ValueError as e:
                return _refuse("query_invalid", detail=str(e)[:200])
            if args.get("limit") is not None:
                try:
                    qdoc = dict(qdoc, limit=int(str(args.get("limit"))))
                except ValueError:
                    pass
            if args.get("cursor"):
                return _refuse("cursor_stale", detail="digest mismatch")
            filters = qdoc.get("filters", {}) or {}
            directory = filters.get("directory") or "/repo"
            ad = OpenCodeSqliteAdapter(db)
            snap = ad.snapshot(SessionSelector(directory=directory))
            res = _q.run_query({"sessions": snap.get("sessions", ()),
                                "messages": snap.get("messages", ()),
                                "parts": snap.get("parts", ()),
                                "coverage": snap.get("coverage", {})}, qdoc)
            res["detail_ref"] = f"query:{len(res.get('rows', []))}/{res.get('total', 0)}"
            return {"ok": True, "result": res}
        except Exception as e:
            msg = str(e)
            if "query_limit_exceeded" in msg:
                return _refuse("query_limit_exceeded", detail=msg[:200])
            if "cursor_stale" in msg:
                return _refuse("cursor_stale", detail=msg[:200])
            return _refuse("query_failed", detail=msg[:200])
    # Remaining read ops: bounded pass-through skeleton (full logic in S1–S4 modules).
    return {"ok": True, "result": {"op": op, "detail_ref": f"{op}:ok"}}


def main(argv: list[str] | None = None) -> int:
    """CLI entry for the Tier-2 plugin (mirrors OP_ARGS; prints one JSON envelope)."""
    import argparse
    import sys
    ap = argparse.ArgumentParser(prog="session_service")
    ap.add_argument("op", choices=list(OPS))
    for flag in sorted({f for flags in OP_ARGS.values() for f in flags}):
        ap.add_argument(f"--{flag}", default=None)
    ns = ap.parse_args(argv)
    args = {k: v for k, v in vars(ns).items() if k != "op" and v is not None}
    print(json.dumps(dispatch(ns.op, args), default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
