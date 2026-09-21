"""text.json_split — rehomed tdd _parse_behaviors recipe (no new logic)."""
import argparse, json


def split_behaviors(text):
    text = text.strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            arr = json.loads(text)
            return [str(x).strip() for x in arr if str(x).strip()]
        except json.JSONDecodeError:
            pass
    out = []
    for line in text.splitlines():
        s = line.strip().lstrip("-*•0123456789.) ").strip()
        if s:
            out.append(s)
    return out


def main():
    ap = argparse.ArgumentParser(description="split JSON array or bullet/newline prose")
    ap.add_argument("--text", default="")
    args = ap.parse_args()
    print(json.dumps({"ok": True, "data": {"behaviors": split_behaviors(args.text)}}))


if __name__ == "__main__":
    main()
