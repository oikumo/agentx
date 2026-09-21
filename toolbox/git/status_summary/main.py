"""git.status_summary — rehomed `git status` recipe (no new logic)."""
import argparse, json, subprocess


def main():
    ap = argparse.ArgumentParser(description="git porcelain status + branch summary")
    ap.add_argument("--short", action="store_true", default=True)
    args = ap.parse_args()
    try:
        out = subprocess.run(
            ["git", "status", "--short", "--branch"],
            capture_output=True, text=True, timeout=15,
        )
        data = {"status": out.stdout.strip(), "rc": out.returncode}
        print(json.dumps({"ok": out.returncode == 0, "data": data}))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
