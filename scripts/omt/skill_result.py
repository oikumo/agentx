#!/usr/bin/env python3
"""skill_result.py — OmtResult envelope v1 (feature_155, stdlib only).

Constructors + validator + adapters. Deterministic, no LLM, no network.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

OUTCOMES = {"succeeded", "blocked", "not_applicable", "inconclusive", "failed"}
CODE_RE = re.compile(r"^[A-Z][A-Z0-9_]+$")
KNOWN_TOP = {
    "ok", "outcome", "code", "data", "blocker", "evidence", "retryable", "stateRevision",
}
KNOWN_BLOCKER = {"gate", "code", "message", "remediation", "requiresApproval"}


def make_succeeded(code: str, evidence: list[str], data=None, stateRevision: str | None = None) -> dict:
    env: dict = {"ok": True, "outcome": "succeeded", "code": code, "evidence": list(evidence), "retryable": False}
    if data is not None:
        env["data"] = data
    if stateRevision is not None:
        env["stateRevision"] = stateRevision
    return env


def make_blocked(code: str, blocker: dict, evidence: list[str], retryable: bool) -> dict:
    return {"ok": False, "outcome": "blocked", "code": code, "blocker": dict(blocker), "evidence": list(evidence), "retryable": bool(retryable)}


def make_not_applicable(code: str, evidence: list[str]) -> dict:
    return {"ok": False, "outcome": "not_applicable", "code": code, "evidence": list(evidence), "retryable": False}


def make_inconclusive(code: str, evidence: list[str]) -> dict:
    return {"ok": False, "outcome": "inconclusive", "code": code, "evidence": list(evidence), "retryable": False}


def make_failed(code: str, message: str, evidence: list[str]) -> dict:
    return {
        "ok": False, "outcome": "failed", "code": code,
        "blocker": {"gate": "skill", "code": code, "message": message, "requiresApproval": False},
        "evidence": list(evidence), "retryable": False,
    }


def validate_envelope(obj: dict) -> list[str]:
    errs: list[str] = []
    if not isinstance(obj, dict):
        return ["ERR envelope: must be object"]
    for k in sorted(obj.keys()):
        if k not in KNOWN_TOP:
            errs.append(f"ERR unknown-field: {k}")
    for f in ("ok", "outcome", "code", "evidence", "retryable"):
        if f not in obj:
            errs.append(f"ERR missing-field: {f}")
    ok = obj.get("ok")
    outcome = obj.get("outcome")
    if not isinstance(ok, bool):
        errs.append("ERR ok: must be boolean")
    if outcome not in OUTCOMES:
        errs.append(f"ERR outcome: must be one of {sorted(OUTCOMES)}")
    code = obj.get("code")
    if not isinstance(code, str) or not CODE_RE.match(code):
        errs.append("ERR code: must match ^[A-Z][A-Z0-9_]+$")
    ev = obj.get("evidence")
    if not isinstance(ev, list) or any(not isinstance(e, str) for e in ev):
        errs.append("ERR evidence: must be string[]")
    if not isinstance(obj.get("retryable"), bool):
        errs.append("ERR retryable: must be boolean")
    if isinstance(ok, bool) and isinstance(outcome, str):
        if ok and outcome != "succeeded":
            errs.append("ERR ok: true only when outcome==succeeded")
        if not ok and outcome == "succeeded":
            errs.append("ERR ok: false when outcome==succeeded")
    if outcome == "blocked":
        bl = obj.get("blocker")
        if not isinstance(bl, dict):
            errs.append("ERR blocker: required when outcome==blocked")
        else:
            for k in sorted(bl.keys()):
                if k not in KNOWN_BLOCKER:
                    errs.append(f"ERR blocker unknown-field: {k}")
            for f in ("gate", "code", "message", "requiresApproval"):
                if f not in bl:
                    errs.append(f"ERR blocker missing-field: {f}")
            if "code" in bl and (not isinstance(bl["code"], str) or not CODE_RE.match(bl["code"])):
                errs.append("ERR blocker code: must match ^[A-Z][A-Z0-9_]+$")
            if "requiresApproval" in bl and not isinstance(bl["requiresApproval"], bool):
                errs.append("ERR blocker requiresApproval: must be boolean")
    sr = obj.get("stateRevision")
    if sr is not None and not isinstance(sr, str):
        errs.append("ERR stateRevision: must be string")
    return errs


def parse_envelope(text: str) -> tuple[dict | None, list[str]]:
    try:
        obj = json.loads(text)
    except Exception as e:
        return None, [f"ERR parse: invalid JSON ({e})"]
    return obj, validate_envelope(obj)


def from_preflight(preflight: dict) -> dict:
    if isinstance(preflight, dict) and preflight.get("ok") is True:
        return make_succeeded("OK", ["omt_status preflight"])
    gate = str(preflight.get("gate", "omt")) if isinstance(preflight, dict) else "omt"
    code = str(preflight.get("code", "GATE_DENIED")) if isinstance(preflight, dict) else "GATE_DENIED"
    msg = str(preflight.get("message", "preflight denied")) if isinstance(preflight, dict) else "preflight denied"
    rem = preflight.get("remediation") if isinstance(preflight, dict) else None
    blocker: dict = {"gate": gate, "code": code, "message": msg, "requiresApproval": bool(preflight.get("requiresApproval", False)) if isinstance(preflight, dict) else False}
    if rem is not None:
        blocker["remediation"] = str(rem)
    return make_blocked(code if CODE_RE.match(code) else "GATE_DENIED", blocker, ["omt_status preflight"], True)


def from_doctor(rc: int, skill_id: str) -> dict:
    if rc == 0:
        return make_succeeded("OK", [f"doctor {skill_id}"])
    return make_failed("DOCTOR_FAILED", f"doctor {skill_id} failed rc={rc}", [f"doctor {skill_id}"])


def from_stop_when(stop: str) -> dict:
    if stop == "operation_succeeds":
        return make_succeeded("OK", [stop])
    if stop in ("same_blocker_survives_legitimate_clearance", "authorization_is_required"):
        blocker = {"gate": "omt", "code": "GATE_DENIED", "message": stop, "requiresApproval": stop == "authorization_is_required"}
        return make_blocked("GATE_DENIED", blocker, [stop], stop != "authorization_is_required")
    if stop == "failure_is_not_an_omt_block":
        return make_not_applicable("NOT_APPLICABLE", [stop])
    return make_inconclusive("INCONCLUSIVE", [stop])


def cmd_validate(path: str) -> int:
    p = Path(path)
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERR parse: invalid JSON ({e})")
        return 2
    errs = validate_envelope(obj)
    if errs:
        print("\n".join(errs))
        return 2
    print("✅ omt-skill-result/v1 OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) == 2 and args[0] == "validate":
        return cmd_validate(args[1])
    if args and args[0] == "make-succeeded":
        code = "OK"
        evidence: list[str] = []
        i = 1
        while i < len(args):
            if args[i] == "--code" and i + 1 < len(args):
                code = args[i + 1]; i += 2
            elif args[i] == "--evidence" and i + 1 < len(args):
                evidence = args[i + 1].split(",") if args[i + 1] else []; i += 2
            else:
                i += 1
        print(json.dumps(make_succeeded(code, evidence), indent=2))
        return 0
    if args and args[0] == "make-blocked":
        code = "GATE_DENIED"; gate = "omt"; message = "blocked"; requires_approval = False
        evidence = []
        i = 1
        while i < len(args):
            if args[i] == "--code" and i + 1 < len(args):
                code = args[i + 1]; i += 2
            elif args[i] == "--gate" and i + 1 < len(args):
                gate = args[i + 1]; i += 2
            elif args[i] == "--message" and i + 1 < len(args):
                message = args[i + 1]; i += 2
            elif args[i] == "--requires-approval":
                requires_approval = True; i += 1
            elif args[i] == "--evidence" and i + 1 < len(args):
                evidence = args[i + 1].split(",") if args[i + 1] else []; i += 2
            else:
                i += 1
        blocker = {"gate": gate, "code": code, "message": message, "requiresApproval": requires_approval}
        print(json.dumps(make_blocked(code, blocker, evidence, True), indent=2))
        return 0
    print("usage: skill_result.py validate <json-file> | make-succeeded --code X --evidence a,b | make-blocked --code X --gate G --message M [--requires-approval]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
