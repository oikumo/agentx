"""Harvest labeled discharge sessions into the real-token ledger (feature_130, sandbox only).

Design: discharge_design.md §4-5 (harvester outline + ledger schema). The DB is
opened READ-ONLY (mode=ro URI); every value comes only from DB columns —
synthetic numbers are never written. Any validation failure exits non-zero with
a named reason and writes NO partial ledger (fail-loudly discipline).

Live-verified implementation decisions (2026-09-26 read-only probes):
- session_input table is EMPTY in this DB -> label path is the design §4.3
  fallback: first line of the first text part of the session's first user
  message (reproduces the known sample ses_f3eb2547bf*).
- session time_created/time_updated are epoch MILLISECONDS -> latency_ms =
  time_updated - time_created (design's "(t_u - t_c) * 1000" assumed seconds
  and would inflate 1000x).

Run: uv run --no-sync python .sandbox/harness_reason/harvest_ledger.py --since <ms>
"""
import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone

ARMS = ("harness", "planner", "kernel")
CASES = ("H1", "H3")
EXPECTED = {(a, c) for a in ARMS for c in CASES}
ROW_ORDER = ("harness:H1", "planner:H1", "kernel:H1", "kernel:H3", "planner:H3", "harness:H3")
LABEL_RE = re.compile(r"^\[harness_reason:discharge arm=(harness|planner|kernel) case=(H1|H3)\]$")
DEFAULT_DB = os.path.expanduser("~/.local/share/opencode/opencode.db")


def repo_root():
    """Project root = two levels up from this script (.sandbox/harness_reason/)."""
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def default_out():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "stage_real_tokens_ledger.json")


def first_user_prompt_text(cur, session_id):
    """First text part of the session's first user message (design §4.3 fallback path).

    message.data and part.data are JSON columns ({role: ...} / {type, text}).
    Returns None when no user message or no text part exists -> no label.
    """
    msgs = cur.execute(
        "SELECT id, data FROM message WHERE session_id = ? ORDER BY time_created ASC, id ASC",
        (session_id,),
    ).fetchall()
    for mid, mdata in msgs:
        try:
            role = json.loads(mdata).get("role")
        except (TypeError, ValueError):
            continue
        if role != "user":
            continue
        for (pdata,) in cur.execute(
            "SELECT data FROM part WHERE message_id = ? ORDER BY time_created ASC, id ASC",
            (mid,),
        ):
            try:
                pd = json.loads(pdata)
            except (TypeError, ValueError):
                continue
            if isinstance(pd, dict) and pd.get("type") == "text" and isinstance(pd.get("text"), str):
                return pd["text"]
        return None  # first user message carries no text part -> no label
    return None


def parse_label(prompt_text):
    """Byte-exact first-line label match (design §1 grammar, closed sets)."""
    if prompt_text is None:
        return None
    first_line = prompt_text.split("\n", 1)[0]
    m = LABEL_RE.match(first_line)
    if m and m.end() == len(first_line):
        return m.group(1), m.group(2)
    return None


def fail(reason, details):
    print(f"HARVEST_FAIL {reason}")
    for d in details:
        print(f"  - {d}")
    print("no ledger written (fail-loudly discipline)")
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description="Harvest labeled discharge sessions into the real-token ledger.")
    ap.add_argument("--since", type=int, required=True,
                    help="capture window start (epoch ms, recorded immediately before spawning batch 1)")
    ap.add_argument("--out", default=default_out(),
                    help=f"ledger output path (default: {default_out()})")
    args = ap.parse_args()

    root = repo_root()
    if not os.path.exists(DEFAULT_DB):
        print(f"HARVEST_FAIL db_not_found: {DEFAULT_DB}")
        sys.exit(2)
    con = sqlite3.connect(f"file:{DEFAULT_DB}?mode=ro", uri=True)
    cur = con.cursor()

    # Candidate child sessions of THIS project created inside the capture window.
    rows = cur.execute(
        """SELECT id, title, agent, model, time_created, time_updated,
                  tokens_input, tokens_output, tokens_reasoning,
                  tokens_cache_read, tokens_cache_write
           FROM session
           WHERE parent_id IS NOT NULL AND directory = ? AND time_created >= ?
           ORDER BY time_created ASC, id ASC""",
        (root, args.since),
    ).fetchall()
    print(f"candidates in window (child sessions of {root} since {args.since}): {len(rows)}")

    labeled = {}
    conflicts = []
    for r in rows:
        sid, title, agent, model, t_created, t_updated, t_in, t_out, t_reason, t_cr, t_cw = r
        label = parse_label(first_user_prompt_text(cur, sid))
        if label is None:
            conflicts.append(f"unlabeled/foreign-label candidate in window: {sid} (title: {str(title)[:80]})")
            continue
        arm, case = label
        if (arm, case) not in EXPECTED:
            fail("unknown(arm_or_case_outside_closed_set)", [f"{sid}: arm={arm} case={case}"])
        if (arm, case) in labeled:
            conflicts.append(f"duplicate label {arm}:{case}: {sid} and {labeled[(arm, case)][0]}")
            continue
        labeled[(arm, case)] = r

    missing = EXPECTED - set(labeled)
    if conflicts or missing:
        det = list(conflicts) + [f"missing label {a}:{c}" for a, c in sorted(missing)]
        fail("harvest_label_conflict", det)

    # Token mapping + validation (design §4.4): values only from DB columns.
    problems = []
    ledger_rows = {}
    for (arm, case), r in labeled.items():
        sid, title, agent, model, t_created, t_updated, t_in, t_out, t_reason, t_cr, t_cw = r
        if not all(isinstance(v, int) for v in (t_in, t_out, t_reason, t_cr)):
            problems.append(("harvest_token_column_invalid",
                             f"{arm}:{case} ({sid}): non-integer token column"))
            continue
        prompt_tokens = t_in + t_cr
        completion_tokens = t_out + t_reason
        if prompt_tokens <= 0 or completion_tokens <= 0:
            problems.append(("harvest_token_column_invalid",
                             f"{arm}:{case} ({sid}): prompt_tokens={prompt_tokens} completion_tokens={completion_tokens} (V8 forbids zero-token measured rows)"))
            continue
        latency_ms = t_updated - t_created  # both columns are epoch ms (live-verified)
        if not isinstance(t_created, int) or not isinstance(t_updated, int) or latency_ms < 0:
            problems.append(("harvest_session_time_invalid",
                             f"{arm}:{case} ({sid}): time_created={t_created} time_updated={t_updated}"))
            continue
        ledger_rows[f"{arm}:{case}"] = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "latency_ms": latency_ms,
            "session_id": sid,
            "label": f"[harness_reason:discharge arm={arm} case={case}]",
            "agent": agent,
            "model": model,
            "time_created": t_created,
        }
    if problems:
        reason = problems[0][0]
        fail(reason, [p for _, p in problems])

    # Ledger (design §5): provenance key is never matched by runner lookups.
    ledger = {
        "provenance": {
            "source": "opencode session DB (~/.local/share/opencode/opencode.db), read-only",
            "harvested_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "capture_window_since_ms": args.since,
            "project_directory": root,
            "mapping": "prompt_tokens = tokens_input + tokens_cache_read; completion_tokens = tokens_output + tokens_reasoning",
            "label_verification": "first line of first text part of first user message (session_input table empty in this DB; design §4.3 fallback path, reproduces known sample ses_f3eb2547bf*)",
            "latency_note": "session time columns are epoch milliseconds; latency_ms = time_updated - time_created (design §4.4 x1000 corrected at implementation)",
            "caveat": "one real session per (arm,case); runner replays each capture across R=3 reps (feature_129 documented caveat)",
        }
    }
    for k in ROW_ORDER:
        ledger[k] = ledger_rows[k]

    with open(args.out, "w") as f:
        json.dump(ledger, f, indent=2)
        f.write("\n")
    con.close()

    print(f"HARVEST_OK 6/6 -> {args.out}")
    for k in ROW_ORDER:
        r = ledger[k]
        total = r["prompt_tokens"] + r["completion_tokens"]
        print(f"  {k}: prompt={r['prompt_tokens']} completion={r['completion_tokens']} "
              f"total={total} latency_ms={r['latency_ms']} agent={r['agent']} "
              f"model={r['model']} session={r['session_id']}")


if __name__ == "__main__":
    main()
# TA: gotcha: gotcha: opencode session time_created/time_updated are epoch MILLISECONDS (not seconds) — latency_ms = time_updated - time_created; discharge_design.md §4.4 "(t_u - t_c) * 1000" would inflate 1000x. Also session_input table is EMPTY in this DB: label verification must go through first user message -> first text part (message.data/part.data are JSON columns, no role/text columns).
