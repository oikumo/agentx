"""git.recent_log — rehomed `git log` recipe (T3 pilot, no new logic class)."""
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
