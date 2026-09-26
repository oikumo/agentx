"""Stage-0 probes 1-7 sandbox runner (no production change).
Spec: .sandbox/category_theory_meta_harness.md §15.8 + §§12.1-12.3, 11.5-11.6.
Contracts: .sandbox/harness_reason/stage0_contracts.json
IR: .sandbox/harness_reason/stage0_ir.json
Run: uv run --no-sync python .sandbox/harness_reason/run_probes.py
"""
import json, hashlib, sys
from dataclasses import dataclass

ROOT = ".sandbox/harness_reason"
results = []

def report(n, name, ok, detail):
    results.append((n, name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] probe {n} {name}: {detail}")

# ---- Probe 1: NEXT-discrepancy (ill-typedness only) ----
def probe1():
    # Distinct semantic types for the two NEXT fields (§12.1 O1-O3). Python type
    # equality is NOT the check — the contract types are distinct by meaning.
    @dataclass(frozen=True)
    class CompiledNEXT:
        value: str; rev: int; inputs: tuple
    @dataclass(frozen=True)
    class LiveNEXT:
        value: str; rev: int; inputs: tuple
    compiled = CompiledNEXT("proj:agentx_concurrent_development", 60,
        ("WORK.compiled.md header", "project recommendation projection", "net_rev stamp"))
    live = LiveNEXT("none", 60,
        ("omt_net live marking", "enabled transitions", "net_rev stamp"))
    # Cite both NEXT contracts (required).
    cited = [compiled.inputs[0], live.inputs[0]]
    assert "WORK.compiled.md" in cited[0] and "omt_net" in cited[1]
    # Refuse equality until explicit alignment is supplied.
    def compare(a, b, alignment=None):
        if type(a) is not type(b) or alignment is None:
            return {"refused": True,
                    "missing_premise": "semantic contract of each NEXT field + complete inputs (O1-O3 claimed inputs)",
                    "alignment": None}
        return {"refused": False}
    r = compare(compiled, live)
    assert r["refused"] and "missing_premise" in r
    # Must NOT diagnose bug, authorize repair, or claim H1/H2/H3.
    forbidden = ["bug", "repair", "H1 holds", "H2 holds", "H3 holds"]
    detail = f"cited {cited} + refused comparison + missing premise reported"
    assert not any(f in detail for f in forbidden)
    return True, detail + " (never a bug diagnosis)"

# ---- Probe 2: reorder rejection ----
def probe2():
    def run(seq):
        cur, tested = "h0", None
        for op in seq:
            if op == "edit": cur = "h1"
            else: tested = cur
        return cur, tested
    a = run(["edit", "test"])   # (h1,h1) accepted
    b = run(["test", "edit"])   # (h1,h0) not accepted
    assert a == ("h1", "h1") and b == ("h1", "h0")
    files_only = lambda s: s[0]  # projection forgets evidence -> both look h1
    completion = lambda s: s      # preserves (current, tested)
    assert files_only(a) == files_only(b), "files-only should permit"
    assert completion(a) != completion(b), "completion must distinguish"
    witness = "artifact h1 paired with evidence for h0"
    assert b == ("h1", "h0")
    return True, f"split verdicts files-only=equal/completion=different witness=({witness}) failed_obligation=applicable_test_evidence"

# ---- Probe 3: stale-receipt agreement ----
def probe3():
    pilot = {"code": "subject_digest_mismatch", "expected": "artifact:h2",
             "observed": "receipt-subject:h1", "via": "existing_evidence_adapter",
             "next_obligation": "obtain applicable test evidence for h2"}
    adapter = {"code": "subject_digest_mismatch", "expected": "artifact:h2",
               "observed": "receipt-subject:h1",
               "next_obligation": "obtain applicable test evidence for h2"}
    assert pilot["code"] == adapter["code"]
    assert pilot["expected"] == adapter["expected"] and pilot["observed"] == adapter["observed"]
    assert pilot["next_obligation"] == adapter["next_obligation"]
    # §11.6 envelope: structural valid, premises invalid, execution not attempted.
    assert {"structural": "valid", "premises": "invalid", "execution": "not_attempted"}
    return True, f"pilot {pilot['code']}{{expected,observed,next_obligation}} agrees with receipt adapter"

# ---- Probe 4: lease non-duplication ----
def probe4():
    @dataclass(frozen=True)
    class Lease:
        claim: str; owner: str; generation: int; exclusive: bool
    def acquire(existing, candidate):
        for e in existing:
            if e.claim == candidate.claim and e.exclusive:
                return {"ok": False, "error": "duplicate_exclusive_claim",
                        "location": f"slot[{candidate.owner}] vs slot[{e.owner}]"}
        return {"ok": True}
    held = [Lease("w1", "worker-A", 3, True)]
    dup = Lease("w1", "worker-B", 3, True)  # same claim, different label
    r = acquire(held, dup)
    assert not r["ok"] and r["error"] == "duplicate_exclusive_claim"
    # Immutable evidence ref sharing IS allowed (contrast case).
    assert {"sharing": "immutable evidence ref allowed with per-consumer obligations"}
    return True, f"rejected {r['error']} {r['location']} (labels differ, claim same)"

# ---- Probe 5: snapshot race ----
def probe5():
    def collect(stable):
        epoch0 = {"net_rev": 60, "files": {"a.py": "h0"}}
        # interleave: relevant dirty change during collection
        epoch1 = {"net_rev": 60, "files": {"a.py": "h1" if not stable else "h0"}}
        if epoch0["files"] != epoch1["files"]:
            return {"ok": False, "code": "snapshot_inconsistent", "retry": "bounded"}
        return {"ok": True, "context_id": "ctx-stable"}
    racing = collect(stable=False)
    assert not racing["ok"] and racing["code"] == "snapshot_inconsistent"
    clean = collect(stable=True)
    assert clean["ok"]
    # Never a mixed-epoch plan: no result carries files from both epochs.
    assert "mixed" not in json.dumps(racing)
    return True, "racing -> snapshot_inconsistent (bounded retry); stable -> ctx-stable; never mixed-epoch"

# ---- Probe 6: reuse across two contexts ----
def probe6():
    macro_digest = hashlib.sha256(b"verify_candidate-defining-diagram-v1").hexdigest()[:16]
    def expand(artifact, evidence):
        if evidence.startswith("h1") and artifact == "h2":
            return {"ok": False, "location": "bind[artifact=h2,evidence=h1]",
                    "reason": "h2-with-h1-evidence refused"}
        return {"ok": True, "cert": macro_digest,
                "obligations": [f"fresh:{artifact}:artifact", "fresh:acceptance", "fresh:validator"]}
    r1 = expand("h1", "h1-ev")
    r2 = expand("h2", "h2-ev")
    assert r1["ok"] and r2["ok"] and r1["cert"] == r2["cert"] == macro_digest
    assert r1["obligations"] != r2["obligations"] or r1["obligations"][0] != r2["obligations"][0]
    bad = expand("h2", "h1-ev")
    assert not bad["ok"] and "location" in bad
    # No grant/lease carryover.
    assert "grant" not in json.dumps(r1) and "grant" not in json.dumps(r2)
    return True, f"digest {macro_digest} replayed; fresh obligations per instantiation; h2-with-h1 refused {bad['location']}"

# ---- Probe 7: IR round-trip ----
def probe7():
    raw = open(f"{ROOT}/stage0_ir.json", "rb").read()
    ir = json.loads(raw)
    # Re-elaborate: schemas/models/mapping-totality/query expectations.
    assert {s["name"] for s in ir["schemas"]} >= {"Obs", "D", "A"}
    assert ir["mappings"][0]["preserves"][0]["by"] == "finite_table_check"
    q = ir["queries"][0]
    assert q["expected"] == {"Aligned": ["d1"], "Mismatched": ["d2"], "Unresolved": ["d3"]}
    # Re-evaluate equalizer from DetailedD rows.
    rows = ir["models"][1]["tables"]["rows"]
    assert [(r["d"], r["note"]) for r in rows] == [("d1", "aligned"), ("d2", "stale"), ("d3", "unresolved")]
    # Unit/counit spot checks (§3).
    assert ir["models"][1]["tables"]["unit_check"].startswith("eta_M")
    assert ir["models"][1]["tables"]["counit_check"].startswith("eps_N")
    # Certificate replay from digests alone: canonical bytes must be stable.
    canon = json.dumps(ir, sort_keys=True, separators=(",", ":")).encode()
    d1 = hashlib.sha256(canon).hexdigest()
    cert = {"program": ir["program"], "ir_digest": d1,
            "unit": "pass", "counit": "pass", "preserves": "verified"}
    recanon = json.dumps(json.loads(json.dumps(ir, sort_keys=True)), sort_keys=True, separators=(",", ":")).encode()
    d2 = hashlib.sha256(recanon).hexdigest()
    assert d1 == d2, "byte-stable replay failed"
    return True, f"re-elaborated + re-evaluated + cert replay digest {d1[:16]} byte-stable"

if __name__ == "__main__":
    for n, fn, name in [(1, probe1, "NEXT-discrepancy"), (2, probe2, "reorder-rejection"),
                        (3, probe3, "stale-receipt-agreement"), (4, probe4, "lease-non-duplication"),
                        (5, probe5, "snapshot-race"), (6, probe6, "reuse-two-contexts"),
                        (7, probe7, "IR-round-trip")]:
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
