"""session.pause_note_append — rehomed pause-note recipe (dry-run default, T1 read-only)."""
import argparse, json
from datetime import datetime, timezone
from pathlib import Path


def repo_root():
    return Path(__file__).resolve().parents[3]


def main():
    ap = argparse.ArgumentParser(description="stage a pause note (dry-run unless --write)")
    ap.add_argument("--note", default="")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = {"ts": ts, "note": args.note}
    if not args.write:
        print(json.dumps({"ok": True, "data": {"dry_run": True, "entry": entry}}))
        return
    outdir = repo_root() / ".sandbox" / "toolbox_runs"
    outdir.mkdir(parents=True, exist_ok=True)
    dest = outdir / f"pause_note_{ts.replace(':', '')}.json"
    dest.write_text(json.dumps(entry, indent=2))
    print(json.dumps({"ok": True, "data": {"dry_run": False, "path": str(dest), "entry": entry}}))


if __name__ == "__main__":
    main()
