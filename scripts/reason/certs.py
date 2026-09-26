"""Reason SSOT — §5 certificate emitter (stdlib only, budgets enforced)."""
import json
import hashlib

SUMMARY_BUDGET = 2048


def make_envelope(program_digest, structural="valid", premises="ok", execution="not_attempted",
                  goal="not_established", issues=None, unknowns=None, derivation=None,
                  context_id="example-context-1", observation_contract="completion-relevant-v1",
                  catalog_version="s0-contracts-v1", model_version="s0-ir-v1",
                  interpreter_version="reason-ssot-v1", unit_counit="checked"):
    issues = issues or []
    unknowns = unknowns or []
    derivation = derivation or [{"rule": "equalizer",
                                 "inputs": ["recorded", "current o source"],
                                 "outputs": ["Aligned", "Mismatched", "Unresolved"]}]
    data = {
        "structural": structural,
        "premises": premises,
        "execution": execution,
        "goal": goal,
        "program_digest": program_digest,
        "catalog_version": catalog_version,
        "model_version": model_version,
        "interpreter_version": interpreter_version,
        "context_id": context_id,
        "observation_contract": observation_contract,
        "unit_counit": unit_counit,
        "issues": issues,
        "unknowns": unknowns,
        "derivation": derivation,
    }
    body = json.dumps(data, sort_keys=True)
    data["certificate_digest"] = "sha256:" + hashlib.sha256(body.encode()).hexdigest()[:16]
    full = json.dumps({"ok": True, "data": data}, sort_keys=True)
    if len(full) <= SUMMARY_BUDGET:
        return {"ok": True, "data": data}
    # Over-budget → summary + mandatory detail_ref, never truncate.
    summary = {
        "structural": structural,
        "premises": premises,
        "goal": goal,
        "program_digest": program_digest,
        "certificate_digest": data["certificate_digest"],
        "issue_count": len(issues),
        "unknown_count": len(unknowns),
        "context_id": context_id,
    }
    ss = json.dumps(summary, sort_keys=True)
    assert len(ss) <= SUMMARY_BUDGET, "summary still over budget"
    return {"ok": True, "summary": summary,
            "detail_ref": f"cert:{data['certificate_digest']}#full",
            "data_digest": data["certificate_digest"]}
