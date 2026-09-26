#!/usr/bin/env python3
"""Reason SSOT CLI — closed enum check|explain|compare|concretize (plan WITHHELD).

Thin callee for reason_check.ts proxy. Stdlib only, advisory, no harness writes.
Run: uv run --no-sync scripts/reason/check.py <op> [--program PATH|JSON] [--node ID] ...
Envelope out: §5 JSON to stdout (ok:true = executed, not valid).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from elaborate import elaborate, digest_of  # noqa: E402
from kernel import evaluate_obs, check_preserves, concretize  # noqa: E402
from router import resolve  # noqa: E402
from certs import make_envelope  # noqa: E402

OPS = ("check", "explain", "compare", "concretize")


def _advisory_fail(reason):
    print(json.dumps({"ok": False, "reason": reason}, sort_keys=True))
    return 2


def op_check(args):
    try:
        ir, prog_digest = elaborate(args.program)
    except ValueError as e:
        return _advisory_fail(f"ill-typed program: {e}")
    except OSError as e:
        return _advisory_fail(f"program unreadable: {e}")
    verdicts = evaluate_obs(ir)
    ok_pres, pres_note = check_preserves(ir)
    issues, unknowns = resolve(ir, context_id=args.context)
    structural = "valid" if ok_pres else "invalid"
    premises = "invalid" if issues else ("unknown" if unknowns else "ok")
    goal = "not_established" if (issues or unknowns) else "established"
    derivation = [{"rule": "equalizer", "inputs": ["recorded", "current o source"],
                   "outputs": [verdicts["Aligned"], verdicts["Mismatched"], verdicts["Unresolved"]]},
                  {"rule": pres_note}]
    env = make_envelope(f"sha256:{prog_digest}", structural=structural, premises=premises,
                        execution="not_attempted", goal=goal, issues=issues, unknowns=unknowns,
                        derivation=derivation, context_id=args.context,
                        observation_contract=args.contract)
    print(json.dumps(env, sort_keys=True))
    return 0


def op_explain(args):
    # Explain needs a prior check envelope: re-run check, then slice by node.
    args.program = args.program
    # Reuse check path to get envelope, then slice.
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = op_check(args)
    try:
        env = json.loads(buf.getvalue())
    except json.JSONDecodeError:
        return _advisory_fail("explain: prior check produced no envelope")
    data = env.get("data") or {}
    node = args.node
    found = [i for i in data.get("issues", []) if i.get("node") == node]
    unk = [u for u in data.get("unknowns", []) if u.get("node") == node]
    if not found and not unk:
        print(json.dumps({"ok": True, "slice": {"node": node, "verdict": "unknown",
                         "reason": "unknown-node", "next_obligation": "provide program containing node",
                         "detail_ref": f"{data.get('program_digest','?')}#{node}"}}, sort_keys=True))
        return 0
    sl = {"node": node, "issues": found, "unknowns": unk,
          "first_unsupported": (found + unk)[0],
          "source_refs": ["stage0_ir.json", "stage0_contracts.json"],
          "permitted_path": "import via existing_test_receipt_adapter/v1, then re-check",
          "detail_ref": f"{data.get('program_digest','?')}#{node}"}
    out = json.dumps({"ok": True, "slice": sl}, sort_keys=True)
    if len(out) > 2048:
        out = json.dumps({"ok": True, "summary": {"node": node, "issue_count": len(found)},
                          "detail_ref": sl["detail_ref"]}, sort_keys=True)
    print(out)
    return rc


def op_compare(args):
    try:
        ir_a, dig_a = elaborate(args.program_a)
        ir_b, dig_b = elaborate(args.program_b)
    except ValueError as e:
        return _advisory_fail(f"ill-typed program: {e}")
    if args.contract not in ("files-only-v1", "completion-relevant-v1"):
        print(json.dumps({"ok": True, "verdict": "unknown",
                          "reason": "unknown-observation-contract",
                          "needed": "files-only-v1|completion-relevant-v1"}, sort_keys=True))
        return 0
    va, vb = evaluate_obs(ir_a), evaluate_obs(ir_b)
    # Pilot rule: files-only contract permits reorder; completion-relevant rejects test;edit under (h1,h0).
    if va == vb and args.contract == "files-only-v1":
        print(json.dumps({"ok": True, "verdict": "equivalent",
                          "contract": args.contract, "digests": [f"sha256:{dig_a}", f"sha256:{dig_b}"]},
                         sort_keys=True))
        return 0
    print(json.dumps({"ok": True, "verdict": "not-equivalent",
                      "contract": args.contract,
                      "witness": {"observed": va, "expected": vb, "pair": "(h1,h0)"},
                      "next_obligation": "obtain applicable test evidence for h2"},
                     sort_keys=True))
    return 0


def op_concretize(args):
    try:
        row = json.loads(args.row)
    except json.JSONDecodeError:
        return _advisory_fail("concretize: --row must be JSON (e.g. '{\"row\":\"d3\"}')")
    reals, info = concretize(row, bound=args.bound)
    if reals is None:
        print(json.dumps({"ok": True, "verdict": "unknown", "unknown": info,
                          "detail_ref": f"concretize#{row.get('row','?')}:bound={args.bound}"},
                         sort_keys=True))
        return 0
    print(json.dumps({"ok": True, "realizations": reals, "distinguishing_info": info,
                      "count": len(reals)}, sort_keys=True))
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="check.py")
    sub = p.add_subparsers(dest="op", required=True)
    c = sub.add_parser("check", help="check program + premises")
    c.add_argument("--program", required=True, help="PATH under .sandbox/harness_reason or raw JSON")
    c.add_argument("--context", default="example-context-1")
    c.add_argument("--contract", default="completion-relevant-v1")
    c.set_defaults(func=op_check)
    e = sub.add_parser("explain", help="slice envelope by node")
    e.add_argument("--program", required=True)
    e.add_argument("--node", required=True)
    e.add_argument("--context", default="example-context-1")
    e.add_argument("--contract", default="completion-relevant-v1")
    e.set_defaults(func=op_explain)
    m = sub.add_parser("compare", help="two programs under named contract")
    m.add_argument("--program-a", required=True)
    m.add_argument("--program-b", required=True)
    m.add_argument("--contract", required=True)
    m.set_defaults(func=op_compare)
    k = sub.add_parser("concretize", help="bounded realizations")
    k.add_argument("--row", required=True, help="JSON e.g. '{\"row\":\"d3\"}'")
    k.add_argument("--bound", type=int, default=8)
    k.set_defaults(func=op_concretize)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.op not in OPS:
        return _advisory_fail(f"unknown op {args.op!r}; closed enum {OPS} (plan withheld)")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
