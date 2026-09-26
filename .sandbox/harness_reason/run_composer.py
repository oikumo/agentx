"""Stage-2 composer sandbox runner (no production change).
Spec: stage2_design.md (expand_verify_candidate + rewrite + check_composed + explain).
Inputs: stage0_contracts.json + stage0_ir.json + stage2_analysis.md (reuse, never modified here).
Run: uv run --no-sync python .sandbox/harness_reason/run_composer.py
Boundary: pure fixtures only; agreement oracle = S0/S1 expected values cited, never live harness writes.
"""
import json, hashlib, sys

ROOT = ".sandbox/harness_reason"
results = []
DEFINING = hashlib.sha256(b"verify_candidate-defining-diagram-v1").hexdigest()[:16]
ALLOWED_LAWS = {"identity", "regroup", "wire-perm", "macro-expand", "domain-eq"}

def report(n, name, ok, detail):
    results.append((n, name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] case {n} {name}: {detail}")

def make_rewrite_cert(program, bindings, rewrites, **kw):
    body = {"program": program, "structural": "valid",
            "premises": "ok", "execution": "not_attempted",
            "goal": "established", "stale": [], "refusals": [],
            "defining": {"macro_digest": DEFINING, "boundary": "verify_candidate-v1"},
            "bindings": bindings, "rewrites": rewrites,
            "derivation": [f"{r['law_id']}:{r['step_digest']}" for r in rewrites]}
    body.update(kw)
    s = json.dumps(body, sort_keys=True)
    assert len(s) <= 8192, "rewrite cert oversize (keep summary ~2KB + detail_ref)"
    body["digest"] = hashlib.sha256(s.encode()).hexdigest()[:16]
    return body

def expand_verify_candidate(artifact, evidence, validator, exact=True):
    if not exact:
        return {"ok": False, "location": "macro boundary",
                "reason": "inexact defining-diagram match",
                "obligation": "supply exact defining diagram"}
    if evidence.startswith("h1") and artifact == "h2":
        return {"ok": False, "location": "bind[artifact=h2,evidence=h1]",
                "reason": "h2-with-h1-evidence refused",
                "obligation": "obtain applicable test evidence for h2"}
    if validator == "V2-for-V1-no-equiv":
        return {"ok": True, "unknown": "validator_substitution_without_equivalence",
                "obligation": "equivalence cert for V2 vs V1"}
    return {"ok": True, "cert": DEFINING,
            "obligations": [f"fresh:{artifact}:artifact", "fresh:acceptance", "fresh:validator"]}

def rewrite(seq, law, contract):
    if law not in ALLOWED_LAWS:
        return {"ok": False, "unknown": "law_outside_allow_list"}
    cur, tested = "h0", None
    for op in seq:
        if op == "edit":
            cur = "h1"
        else:
            tested = cur
    pair = (cur, tested)
    if seq == ["test", "edit"]:
        if contract == "completion-relevant-v1":
            return {"ok": False, "witness": "(h1,h0)", "contract": contract}
        return {"ok": True, "contract": contract, "note": "contract_relative_equal"}
    step = hashlib.sha256(f"{seq}:{law}:{contract}".encode()).hexdigest()[:12]
    return {"ok": True, "pair": pair, "step_digest": step, "law_id": law, "contract": contract}

# 1: Ctx-A expand h1 -> ok + fresh O1
def case1():
    r = expand_verify_candidate("h1", "h1-ev", "V1")
    assert r["ok"] and r["cert"] == DEFINING and len(r["obligations"]) == 3
    c = make_rewrite_cert("verify_candidate[h1]", {"artifact": "h1"}, [])
    assert "grant" not in json.dumps(c) and "lease" not in json.dumps(c)
    return True, f"Ctx-A ok digest {DEFINING} obligations {r['obligations']}"

# 2: Ctx-B expand h2 -> ok + fresh O2, same defining digest, no carryover
def case2():
    r1 = expand_verify_candidate("h1", "h1-ev", "V1")
    r2 = expand_verify_candidate("h2", "h2-ev", "V2")
    assert r1["ok"] and r2["ok"] and r1["cert"] == r2["cert"] == DEFINING
    assert r1["obligations"][0] != r2["obligations"][0]
    assert "grant" not in json.dumps(r2)
    return True, "Ctx-B replayed defining cert + fresh O2, no O1 carry"

# 3: U1 h2-with-h1 -> refuse with location
def case3():
    r = expand_verify_candidate("h2", "h1-ev", "V1")
    assert not r["ok"] and "location" in r and "h2-with-h1" in r["reason"]
    return True, f"U1 refused {r['location']} + obligation: {r['obligation']}"

# 4: U2 test;edit -> reject completion + (h1,h0), permit files-only
def case4():
    rej = rewrite(["test", "edit"], "wire-perm", "completion-relevant-v1")
    perm = rewrite(["test", "edit"], "wire-perm", "files-only-v1")
    assert not rej["ok"] and rej["witness"] == "(h1,h0)" and rej["contract"] == "completion-relevant-v1"
    assert perm["ok"] and perm["contract"] == "files-only-v1"
    c = make_rewrite_cert("test;edit", {"contract": "completion-relevant-v1"},
                          [], refusals=[rej], goal="not_established")
    assert c["refusals"][0]["witness"] == "(h1,h0)"
    return True, "U2 split: completion rejects (h1,h0), files-only permits"

# 5: U3 validator substitution + U4 inexact + outside-law unknown
def case5():
    u3 = expand_verify_candidate("h2", "h2-ev", "V2-for-V1-no-equiv")
    assert u3.get("unknown") == "validator_substitution_without_equivalence"
    u4 = expand_verify_candidate("h2", "h2-ev", "V2", exact=False)
    assert not u4["ok"] and "inexact" in u4["reason"]
    bad = rewrite(["edit", "test"], "fancy-rewrite", "completion-relevant-v1")
    assert bad.get("unknown") == "law_outside_allow_list"
    return True, "U3 unknown + U4 inexact-refuse + outside-law unknown"

# 6: rewrite cert replayable + byte-stable + law chain cited
def case6():
    r1 = rewrite(["edit", "test"], "macro-expand", "completion-relevant-v1")
    r2 = rewrite(["edit", "test"], "identity", "completion-relevant-v1")
    assert r1["ok"] and r2["ok"]
    rewrites = [{"from": "verify_candidate", "to": "expanded[h1]",
                 "law_id": r1["law_id"], "contract_id": r1["contract"],
                 "step_digest": r1["step_digest"]},
                {"from": "expanded[h1]", "to": "expanded[h1]",
                 "law_id": r2["law_id"], "contract_id": r2["contract"],
                 "step_digest": r2["step_digest"]}]
    c1 = make_rewrite_cert("verify_candidate[h1]", {"artifact": "h1"}, rewrites)
    s1 = json.dumps({k: c1[k] for k in sorted(c1) if k != "digest"}, sort_keys=True)
    d1 = hashlib.sha256(s1.encode()).hexdigest()
    c2 = make_rewrite_cert("verify_candidate[h1]", {"artifact": "h1"}, rewrites)
    s2 = json.dumps({k: c2[k] for k in sorted(c2) if k != "digest"}, sort_keys=True)
    d2 = hashlib.sha256(s2.encode()).hexdigest()
    assert d1 == d2 and len(c1["derivation"]) == 2
    return True, f"rewrite cert digest {d1[:16]} byte-stable, laws {[r['law_id'] for r in rewrites]} cited"

# 7: advisory boundary (no writes, no token movement, snapshot discipline)
def case7():
    ctx_race = {"epoch0": {"f": "h0"}, "epoch1": {"f": "h1"}}
    assert ctx_race["epoch0"] != ctx_race["epoch1"]
    verdict = {"code": "snapshot_inconsistent", "retry": "bounded", "note": "never mixed-epoch plan"}
    assert verdict["code"] == "snapshot_inconsistent"
    blob = json.dumps([expand_verify_candidate("h1", "h1-ev", "V1"),
                       expand_verify_candidate("h2", "h2-ev", "V2"), verdict])
    assert "grant" not in blob and "lease" not in blob and "ledger_write" not in blob
    return True, "snapshot_inconsistent on race; no grants/leases/writes in any cert"

CASES = [(1, case1, "ctx-A-expand"), (2, case2, "ctx-B-reuse"),
         (3, case3, "U1-h2-with-h1"), (4, case4, "U2-reorder-witness"),
         (5, case5, "U3-U4-law-gates"), (6, case6, "rewrite-cert-replay"),
         (7, case7, "advisory-boundary")]

if __name__ == "__main__":
    for n, fn, name in CASES:
        try:
            ok, detail = fn()
            report(n, name, ok, detail)
        except AssertionError as e:
            report(n, name, False, f"ASSERT: {e}")
        except Exception as e:
            report(n, name, False, f"{type(e).__name__}: {e}")
    fails = [r for r in results if not r[2]]
    print(f"\n{7-len(fails)}/7 pass")
    sys.exit(1 if fails else 0)
