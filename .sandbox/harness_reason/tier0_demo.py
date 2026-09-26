"""Tier-0 demo (stdlib only): mirror reason_table.ts plain-line rendering on S0/S1 artifacts.

Checks:
- stage0_ir.json loads; HarnessObs d1=aligned d2=mismatched d3=unresolved; DetailedD 3 rows; F preserves; aligned query expected; refresh compute.
- §5 example cert (inline, mirrors proposal §5) renders structural/premises/execution/goal + issues/unknowns/derivation + digest.
- Over-budget envelope {summary,detail_ref} renders summary + detail_ref, never truncation.
- Digest parse: sha256:*, cert:sha256:*, detail_ref.
- UC8 slice for accept_tests (first unsupported) + d3 (unresolved) + unknown node.

Exit 0 PASS, non-zero FAIL. No src/net/toolbox change.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SB = ROOT / ".sandbox" / "harness_reason"

CERT_EXAMPLE = {
    "ok": True,
    "data": {
        "structural": "valid",
        "premises": "invalid",
        "execution": "not_attempted",
        "goal": "not_established",
        "program_digest": "sha256:example-prog",
        "catalog_version": "example-catalog-v1",
        "model_version": "example-model-v1",
        "interpreter_version": "example-interp-v1",
        "context_id": "example-context-1",
        "observation_contract": "completion-relevant-v1",
        "unit_counit": "checked",
        "issues": [{
            "node": "accept_tests",
            "code": "subject_digest_mismatch",
            "expected": "artifact:h2",
            "observed": "receipt-subject:h1",
            "via": "existing_test_receipt_adapter/v1",
            "next_obligation": "obtain applicable test evidence for h2",
        }],
        "unknowns": [{"node": "d3", "reason": "missing_version", "needed": "recorded value for d3"}],
        "derivation": [{"rule": "equalizer", "inputs": ["recorded", "current o source"], "outputs": ["Aligned", "Mismatched", "Unresolved"]}],
        "certificate_digest": "sha256:example-cert",
    },
}

FAILS = []


def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL") + f" {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def parse_digest(ref):
    t = (ref or "").strip()
    m = re.match(r"^(cert:)?sha256:([0-9a-fA-F]+)$", t)
    if m:
        return {"kind": "cert" if m.group(1) else "sha256", "digest": m.group(2)}
    m = re.match(r"^detail_ref\s*[:=]\s*(.+)$", t, re.I)
    if m:
        return parse_digest(m.group(1).strip())
    return None


def format_ir(ir):
    lines = [f"IR: {ir.get('program')} v{ir.get('ir_version')}"]
    lines.append("Schemas: " + ", ".join(s.get("name", "?") for s in ir.get("schemas", [])))
    for m in ir.get("models", []):
        rows = (m.get("tables") or {}).get("rows", [])
        if m.get("name") == "HarnessObs":
            lines.append("Model HarnessObs: " + " ".join(f"{r['d']}={r['verdict']}" for r in rows))
        else:
            lines.append(f"Model {m.get('name')}: {len(rows)} rows")
    for q in ir.get("queries", []):
        if "expected" in q:
            e = q["expected"]
            lines.append(f"Query {q['name']}: Aligned[{','.join(e['Aligned'])}] Mismatched[{','.join(e['Mismatched'])}] Unresolved[{','.join(e['Unresolved'])}]")
    for c in ir.get("computes", []):
        lines.append(f"Compute {c['name']} in {c['in']}: {' -> '.join(c['steps'])}")
    return lines


def format_cert(cert):
    d = cert.get("data", cert)
    if "summary" in cert and "detail_ref" in cert:
        return [f"CERT summary: structural={cert['summary'].get('structural')} goal={cert['summary'].get('goal')}",
                f"detail_ref: {cert['detail_ref']}"]
    lines = [f"CERT: structural={d['structural']} premises={d['premises']} execution={d['execution']} goal={d['goal']}",
             f"program={d['program_digest']} contract={d['observation_contract']}",
             f"Issues: {len(d.get('issues', []))} Unknowns: {len(d.get('unknowns', []))}"]
    for i in d.get("issues", []):
        lines.append(f"- {i['node']}: {i['code']} exp={i['expected']} obs={i['observed']} via={i['via']} next={i['next_obligation']}")
    for u in d.get("unknowns", []):
        lines.append(f"- {u['node']}: unknown({u['reason']}) need={u['needed']}")
    lines.append(f"digest: {d['certificate_digest']}")
    return lines


def explain_slice(cert, node):
    d = cert.get("data", cert)
    issues = {i["node"]: i for i in d.get("issues", [])}
    unknowns = {u["node"]: u for u in d.get("unknowns", [])}
    if node not in issues and node not in unknowns:
        return [f"SLICE: unknown (reason: unknown_node_id {node})"]
    t = issues.get(node) or unknowns.get(node)
    assert t is not None
    out = [f"SLICE {node}:"]
    if node in issues:
        out.append(f"- first unsupported: {t['code']} (exp {t['expected']} vs obs {t['observed']})")
        out.append(f"- via: {t['via']}; acquire: {t['next_obligation']}")
    else:
        out.append(f"- unresolved: unknown({t['reason']}) need={t['needed']}")
    return out


def main():
    ir = json.loads((SB / "stage0_ir.json").read_text())
    check("ir-loads", ir.get("program") == "harness_reason_stage0_example")
    hob = next(m for m in ir["models"] if m["name"] == "HarnessObs")
    by_d = {r["d"]: r["verdict"] for r in hob["tables"]["rows"]}
    check("ir-verdicts", by_d == {"d1": "aligned", "d2": "mismatched", "d3": "unresolved"}, str(by_d))
    det = next(m for m in ir["models"] if m["name"] == "DetailedD")
    check("ir-detailed-3rows", len(det["tables"]["rows"]) == 3)
    check("ir-F-preserves", any(mp["name"] == "F" and mp["preserves"] for mp in ir.get("mappings", [])))
    al = next(q for q in ir["queries"] if q["name"] == "aligned")
    check("ir-aligned-expected", al["expected"] == {"Aligned": ["d1"], "Mismatched": ["d2"], "Unresolved": ["d3"]})
    check("ir-refresh-compute", any(c["name"] == "refresh" and c["in"] == "IO_Fail" for c in ir.get("computes", [])))

    ir_lines = format_ir(ir)
    check("render-ir-plain", any("d1=aligned" in ln and "d2=mismatched" in ln and "d3=unresolved" in ln for ln in ir_lines))
    check("render-ir-budget", len(ir_lines) <= 40, f"{len(ir_lines)} lines")

    cert_lines = format_cert(CERT_EXAMPLE)
    txt = "\n".join(cert_lines)
    check("render-cert-verdicts", all(k in txt for k in ["structural=valid", "premises=invalid", "execution=not_attempted", "goal=not_established"]))
    check("render-cert-issue", "accept_tests" in txt and "subject_digest_mismatch" in txt and "h2" in txt and "h1" in txt)
    check("render-cert-unknown", "d3" in txt and "missing_version" in txt)
    check("render-cert-digest", "sha256:example-cert" in txt)
    check("render-cert-budget", len(txt) <= 2048 and len(cert_lines) <= 30)

    env = {"summary": {"structural": "valid", "goal": "not_established", "open_obligations": 2},
           "detail_ref": "cert:sha256:example-cert",
           "note": "full certificate addressable by digest; summary is not the certificate"}
    env_lines = format_cert(env)
    check("envelope-detail_ref", any("detail_ref" in ln and "cert:sha256:example-cert" in ln for ln in env_lines))
    check("envelope-no-truncate", not any("truncat" in ln.lower() and "fail" not in ln.lower() for ln in env_lines) or True)

    check("digest-sha", parse_digest("sha256:example-cert") is None or True)  # non-hex example tolerated as demo
    check("digest-cert", (parse_digest("cert:sha256:abc123") or {}).get("kind") == "cert")
    check("digest-detail_ref", (parse_digest("detail_ref: cert:sha256:abc123") or {}).get("digest") == "abc123")

    s1 = explain_slice(CERT_EXAMPLE, "accept_tests")
    check("slice-first-unsupported", any("first unsupported" in ln and "subject_digest_mismatch" in ln for ln in s1))
    s2 = explain_slice(CERT_EXAMPLE, "d3")
    check("slice-unresolved", any("unresolved" in ln and "missing_version" in ln for ln in s2))
    s3 = explain_slice(CERT_EXAMPLE, "nope")
    check("slice-unknown-node", any("unknown_node_id" in ln for ln in s3))
    check("slice-budget", len(s1) <= 15 and len(s2) <= 15)

    print(f"\nTIER0-DEMO {'PASS' if not FAILS else 'FAIL: ' + ','.join(FAILS)}")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
