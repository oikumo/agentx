"""ledger.window_slice — rehomed ledger tail recipe (no new logic)."""
import argparse, json
from pathlib import Path


def repo_root():
    # toolbox/ledger/window_slice/main.py -> root (4 up)
    return Path(__file__).resolve().parents[3]


def main():
    ap = argparse.ArgumentParser(description="slice last N ledger lines")
    ap.add_argument("--lines", type=int, default=5)
    ap.add_argument("--kind", default="")
    args = ap.parse_args()
    ledger = repo_root() / ".meta" / ".omt" / "ledger.jsonl"
    try:
        lines = ledger.read_text().splitlines() if ledger.exists() else []
        if args.kind:
            lines = [ln for ln in lines if f'"kind":"{args.kind}"' in ln or f'"kind": "{args.kind}"' in ln]
        data = {"ledger": str(ledger), "total": len(lines), "slice": lines[-args.lines:]}
        print(json.dumps({"ok": True, "data": data}))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
