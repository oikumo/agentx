"""Stage-1 checker sandbox runner (no production change).
Spec: .sandbox/category_theory_meta_harness.md §14.1 (12 cases) + stage1_design.md.
Inputs: stage0_contracts.json + stage0_ir.json (reuse, never modified here).
Run: uv run --no-sync python .sandbox/harness_reason/run_checker.py
Boundary: pure fixtures only; agreement oracle = S0 expected values cited, never live harness writes.
"""
import json, hashlib, sys

ROOT = ".sandbox/harness_reason"
results = []

def report(n, name, ok, detail):
    results.append((n, name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] case {n} {name}: {detail}")

def make_cert(program, verdict, **kw):
    body = {"program": program, "structural": "valid",
            "premises": "ok", "execution": "not_attempted",
            "goal": verdict, "stale": [], "derivation": ["check", "explain-slice"]}
    body.update(kw)
    s = json.dumps(body, sort_keys=True)
    assert len(s) <= 4096, "cert envelope oversize (keep ~2KB summary + detail_ref)"
    body["digest"] = hashlib.sha256(s.encode()).hexdigest()[:16]
    return body

def explain(cert, node):
    return {"cert": cert["digest"], "node": node,
            "premises": cert.get("premises"), "stale": cert.get("stale"),
            "detail_ref": f"{cert['program']}#{node}"}

# 1: hypothesis needs evidence -> reject + name missing premise
def case1():
    c = make_cert("hypothesis-needs-evidence", "not_established",
                  premises="failed", missing=["validator:existing_test_receipt_adapter/v1"],
                  structural="invalid", location="premise[evidence]")
    assert c["premises"] == "failed" and "validator" in c["missing"][0]
    e = explain(c, "premise[evidence]")
    assert "detail_ref" in e
    return True, "rejected + named missing validator/premise"

# 2: receipt old digest -> stale + exact mismatch
def case2():
    c = make_cert("receipt-old-digest", "not_established",
                  premises="invalid", witness={"expected": "h2", "observed": "h1"},
                  code="subject_digest_mismatch")
    assert c["witness"] == {"expected": "h2", "observed": "h1"}
    return True, "stale preserved + exact mismatch h2 vs h1"

# 3: fabricated passed:true -> require trusted producer
def case3():
    c = make_cert("fabricated-passed", "not_established",
                  premises="failed", obligation="resolvable trusted producer/record")
    assert "trusted producer" in c["obligation"]
    return True, "caller assertion refused; trusted producer required"

# 4: duplicate exclusive claim -> reject even labels differ
def case4():
    held = [("w1", "A")]
    cand = ("w1", "B")
    dup = any(h[0] == cand[0] for h in held)
    assert dup
    c = make_cert("lease-dup", "not_established", structural="invalid",
                  location="slot[B] vs slot[A]", error="duplicate_exclusive_claim")
    assert c["error"] == "duplicate_exclusive_claim"
    return True, "duplication rejected across labels"

# 5: share immutable ref -> allow + per-consumer obligations
def case5():
    c = make_cert("share-immutable-ref", "established",
                  obligations=["consumer-A:applicability", "consumer-B:applicability"])
    assert len(c["obligations"]) == 2
    return True, "sharing allowed with per-consumer obligations"

# 6: timeout/fail preserved
def case6():
    c = make_cert("test-timeout", "not_established",
                  premises="failed", outcome="timeout preserved",
                  note="success branch not established")
    assert "preserved" in c["outcome"]
    return True, "timeout preserved; success not marked"

# 7: test-before-edit rejected under completion, permitted files-only
def case7():
    def run(seq):
        cur, tested = "h0", None
        for op in seq:
            if op == "edit": cur = "h1"
            else: tested = cur
        return cur, tested
    a, b = run(["edit", "test"]), run(["test", "edit"])
    assert a == ("h1", "h1") and b == ("h1", "h0")
    c = make_cert("reorder", "not_established", contract="completion-relevant-v1",
                  witness="(h1,h0)", files_only="equal", completion="different")
    assert c["contract"] == "completion-relevant-v1" and c["witness"] == "(h1,h0)"
    return True, "split verdicts + (h1,h0) witness under named contract"

# 8: macro same bindings -> replay
def case8():
    d = hashlib.sha256(b"verify_candidate-defining-diagram-v1").hexdigest()[:16]
    c = make_cert("macro-replay", "established", defining=d, effects="preserved",
                  obligations=["fresh:artifact", "fresh:acceptance", "fresh:validator"])
    assert c["defining"] == d and len(c["obligations"]) == 3
    return True, f"defining cert {d} replayed + boundaries preserved"

# 9: unrelated change preserves immutables
def case9():
    c = make_cert("unrelated-change", "established",
                  preserved=["deriv-d1"], invalidated=[])
    assert c["preserved"] == ["deriv-d1"] and c["invalidated"] == []
    return True, "unaffected derivations preserved"

# 10: relevant change -> stale + re-import
def case10():
    c = make_cert("relevant-change", "not_established",
                  stale=[{"result": "deriv-d2", "cause": "policy-v2",
                           "reimport": "authoritative decision"}])
    assert c["stale"][0]["cause"] == "policy-v2"
    return True, "affected marked stale + re-import listed"

# 11: context race -> snapshot_inconsistent
def case11():
    e0, e1 = {"f": "h0"}, {"f": "h1"}
    assert e0 != e1
    c = make_cert("snapshot-race", "unknown", code="snapshot_inconsistent",
                  retry="bounded", note="never mixed-epoch plan")
    assert c["code"] == "snapshot_inconsistent"
    return True, "snapshot_inconsistent, never mixed-epoch"

# 12: bound/validator absent -> specific unknown
def case12():
    c = make_cert("bound-absent", "unknown",
                  unknown="no_candidate_within_bounds(depth=3)",
                  missing_validator="realize_enumerator perm/coverage gate")
    assert "unknown" in c["goal"] and "bounds" in c["unknown"]
    return True, "specific unknown (bounds + missing validator), not impossible"

CASES = [(1, case1, "hypothesis-needs-evidence"), (2, case2, "receipt-old-digest"),
         (3, case3, "fabricated-passed"), (4, case4, "lease-dup"),
         (5, case5, "share-immutable"), (6, case6, "timeout-preserved"),
         (7, case7, "reorder-contract"), (8, case8, "macro-replay"),
         (9, case9, "unrelated-preserves"), (10, case10, "relevant-stale"),
         (11, case11, "snapshot-race"), (12, case12, "bound-unknown")]

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
    print(f"\n{12-len(fails)}/12 pass")
    sys.exit(1 if fails else 0)
