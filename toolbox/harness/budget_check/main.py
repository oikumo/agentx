"""harness.budget_check — rehomed `harnessc check` recipe (no new logic)."""
import argparse, json, subprocess
from pathlib import Path


def repo_root():
    return Path(__file__).resolve().parents[3]


def main():
    ap = argparse.ArgumentParser(description="harness budget check wrapper")
    ap.parse_args()
    try:
        out = subprocess.run(
            ["uv", "run", "scripts/omt/harnessc.py", "check"],
            capture_output=True, text=True, timeout=60,
            cwd=str(repo_root()),
        )
        tail = (out.stdout + out.stderr).strip().splitlines()[-5:]
        print(json.dumps({"ok": out.returncode == 0, "data": {"rc": out.returncode, "tail": tail}}))
        raise SystemExit(out.returncode)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
