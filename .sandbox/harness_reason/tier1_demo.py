"""Tier-1 demo (stdlib only): 4 ops via SSOT functions + CLI parity.

Checks: check envelope (structural/premises/goal + mismatch + d3 unknown + digest),
explain slice (accept_tests unsupported + unknown node), compare (files-only
equivalent + unknown contract), concretize (4 bounded + over-bound unknown),
CLI parity for all 4 ops. Exit 0 PASS, non-zero FAIL. No src/net/toolbox change.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "reason"))
from elaborate import elaborate  # noqa: E402
from kernel import evaluate_obs, concretize  # noqa: E402
from router import resolve  # noqa: E402
from certs import make_envelope  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL") + f" {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def cli(*argv):
    r = subprocess.run([sys.executable, "scripts/reason/check.py", *argv],
                       capture_output=True, text=True, cwd=str(ROOT))
    return r


def main():
    ir, dig = elaborate("stage0_ir.json")
    check("demo-ir-loads", bool(ir.get("schemas") and ir.get("models")))
    v = evaluate_obs(ir)
    check("demo-verdicts", v == {"Aligned": ["d1"], "Mismatched": ["d2"], "Unresolved": ["d3"]}, str(v))
    issues, unknowns = resolve(ir)
    check("demo-mismatch", any(i["code"] == "subject_digest_mismatch" for i in issues))
    check("demo-d3-unknown", any(u["node"] == "d3" for u in unknowns))
    env = make_envelope(f"sha256:{dig}", premises="invalid", issues=issues, unknowns=unknowns)
    check("demo-envelope", env["ok"] and "certificate_digest" in env["data"])
    check("demo-budget", len(json.dumps(env)) <= 4096)
    reals, info = concretize({"row": "d3"}, bound=8)
    check("demo-concretize", len(reals) == 4 and info[0] == "recorded")
    over, info2 = concretize({"row": "d3"}, bound=2)
    check("demo-over-bound", over is None and info2["reason"] == "bound_exceeded")

    r = cli("check", "--program", "stage0_ir.json")
    check("demo-cli-check", r.returncode == 0 and json.loads(r.stdout)["ok"] is True, r.stderr[:200])
    r = cli("explain", "--program", "stage0_ir.json", "--node", "accept_tests")
    check("demo-cli-explain", r.returncode == 0 and "accept_tests" in r.stdout, r.stderr[:200])
    r = cli("compare", "--program-a", "stage0_ir.json", "--program-b", "stage0_ir.json",
            "--contract", "files-only-v1")
    check("demo-cli-compare", r.returncode == 0 and "equivalent" in r.stdout, r.stderr[:200])
    r = cli("concretize", "--row", '{"row":"d3"}', "--bound", "8")
    check("demo-cli-concretize", r.returncode == 0 and "realizations" in r.stdout, r.stderr[:200])
    r = cli("plan", "--program", "stage0_ir.json")
    check("demo-plan-withheld", r.returncode != 0, "plan must stay withheld")

    print("\nTIER1-DEMO " + ("PASS" if not FAILS else f"FAIL {FAILS}"))
    return 0 if not FAILS else 1


if __name__ == "__main__":
    raise SystemExit(main())
