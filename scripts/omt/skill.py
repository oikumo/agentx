#!/usr/bin/env python3
"""skill.py — OpenCode skill scaffolder/validator (feature_154, stdlib only).

Commands: doctor|new|test|list. Deterministic, no LLM, no network.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILLS_DIRS = [REPO / ".opencode" / "skills", REPO / ".agents" / "skills"]
KNOWN_OPS = {
    "omt_status.preflight",
    "omt_q.state",
    "omt_q.plan",
    "omt_nav.nav",
    "omt_kb_nav.nav",
    "omt_phase.declare",
    "omt_tdd.testlist",
    "omt_net.probe",
}
KNOWN_RESULT_SCHEMAS = {"omt-skill-result/v1"}
REQUIRED_FORBIDDEN = {"weaken_gate", "forge_receipt", "expand_scope_without_authority"}
ID_RE = re.compile(r"^[a-z0-9-]+$")
VER_RE = re.compile(r"^0\.[0-9]+\.[0-9]+$")
KNOWN_TOP = {
    "schema_version", "id", "version", "mode", "inputs", "requires",
    "allowed_effects", "forbidden_effects", "state_owner", "result_schema", "stop_when",
}


def find_skill_dir(skill_id: str) -> Path | None:
    for base in SKILLS_DIRS:
        cand = base / skill_id
        if (cand / "SKILL.md").exists():
            return cand
    return None


def load_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    body = text[3:end]
    out: dict = {}
    key = None
    for line in body.splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            k, v = line.split(":", 1)
            key = k.strip()
            out[key] = v.strip()
        elif key:
            out[key] = (out.get(key, "") + "\n" + line.strip()).strip()
    return out


def validate_contract(contract: dict, skill_dir_name: str) -> list[str]:
    errs: list[str] = []
    if not isinstance(contract, dict):
        return ["ERR contract: must be object"]
    for k in sorted(contract.keys()):
        if k not in KNOWN_TOP:
            errs.append(f"ERR unknown-field: {k}")
    for f in sorted(KNOWN_TOP):
        if f not in contract:
            errs.append(f"ERR missing-field: {f}")
    if contract.get("schema_version") != "1":
        errs.append("ERR schema_version: must be '1'")
    cid = contract.get("id")
    if not isinstance(cid, str) or not ID_RE.match(cid):
        errs.append("ERR id: must match ^[a-z0-9-]+$")
    elif cid != skill_dir_name:
        errs.append(f"ERR id-mismatch: contract id '{cid}' != dir '{skill_dir_name}'")
    ver = contract.get("version", "")
    if not isinstance(ver, str) or not VER_RE.match(ver):
        errs.append("ERR version: must be 0.x.y")
    if contract.get("mode") != "procedural":
        errs.append("ERR mode: must be 'procedural'")
    if not isinstance(contract.get("inputs"), list) or len(contract.get("inputs", [])) < 1:
        errs.append("ERR inputs: need >=1")
    req = contract.get("requires", [])
    if not isinstance(req, list):
        errs.append("ERR requires: must be list")
    else:
        for op in req:
            if op not in KNOWN_OPS:
                errs.append(f"ERR requires: unknown op '{op}'")
    forb = set(contract.get("forbidden_effects", []) or [])
    missing = REQUIRED_FORBIDDEN - forb
    if missing:
        errs.append(f"ERR forbidden_effects: missing {sorted(missing)}")
    if contract.get("state_owner") != "external":
        errs.append("ERR state_owner: must be 'external'")
    if contract.get("result_schema") not in KNOWN_RESULT_SCHEMAS:
        errs.append("ERR result_schema: must be 'omt-skill-result/v1'")
    stop = contract.get("stop_when", [])
    if not isinstance(stop, list) or len(stop) < 2:
        errs.append("ERR stop_when: need >=2")
    return errs


def cmd_doctor(skill_id: str) -> int:
    d = find_skill_dir(skill_id)
    if d is None:
        print(f"ERR not-found: {skill_id}")
        return 2
    fm = load_frontmatter(d / "SKILL.md")
    errs: list[str] = []
    if fm.get("name") != skill_id:
        errs.append(f"ERR frontmatter: name '{fm.get('name')}' != dir '{skill_id}'")
    desc = fm.get("description", "")
    if len(desc) < 20:
        errs.append("ERR frontmatter: description >=20 chars")
    cpath = d / "skill.contract.json"
    if not cpath.exists():
        errs.append("ERR contract: missing skill.contract.json")
    else:
        try:
            contract = json.loads(cpath.read_text(encoding="utf-8"))
        except Exception as e:
            errs.append(f"ERR contract: invalid JSON ({e})")
            contract = None
        if contract is not None:
            errs.extend(validate_contract(contract, d.name))
    if errs:
        print("\n".join(errs))
        return 2
    print(f"✅ {skill_id} contract OK")
    return 0


def cmd_new(skill_id: str) -> int:
    if not ID_RE.match(skill_id):
        print(f"ERR id: '{skill_id}' must match ^[a-z0-9-]+$")
        return 2
    dest = REPO / ".opencode" / "skills" / skill_id
    if dest.exists():
        print(f"ERR exists: .opencode/skills/{skill_id}")
        return 2
    (dest / "references").mkdir(parents=True)
    (dest / "references" / ".gitkeep").write_text("", encoding="utf-8")
    (dest / "SKILL.md").write_text(
        f"---\nname: {skill_id}\ndescription: >\n  TODO describe when OpenCode should load this skill.\n---\n\n"
        f"# {skill_id}\n\n## Use when\n\nTODO.\n\n## Do not use when\n\nTODO.\n\n"
        "## Procedure\n\n1. TODO.\n\n## Stop\n\nTODO stop conditions.\n",
        encoding="utf-8",
    )
    contract = {
        "schema_version": "1", "id": skill_id, "version": "0.1.0", "mode": "procedural",
        "inputs": ["TODO"], "requires": ["omt_status.preflight"],
        "allowed_effects": ["read_harness_state"],
        "forbidden_effects": sorted(REQUIRED_FORBIDDEN),
        "state_owner": "external", "result_schema": "omt-skill-result/v1",
        "stop_when": ["TODO_done", "TODO_blocked"],
    }
    (dest / "skill.contract.json").write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    print(f"✅ created .opencode/skills/{skill_id}/")
    return 0


def cmd_test(skill_id: str) -> int:
    return cmd_doctor(skill_id)


def cmd_list() -> int:
    found: dict[str, str] = {}
    for base in SKILLS_DIRS:
        if not base.exists():
            continue
        for child in sorted(p for p in base.iterdir() if p.is_dir()):
            if not (child / "SKILL.md").exists():
                continue
            cpath = child / "skill.contract.json"
            if not cpath.exists():
                found.setdefault(child.name, "contract-missing")
            else:
                try:
                    contract = json.loads(cpath.read_text(encoding="utf-8"))
                except Exception:
                    found.setdefault(child.name, "contract-invalid")
                    continue
                errs = validate_contract(contract, child.name)
                found.setdefault(child.name, "contract-ok" if not errs else "contract-invalid")
    for k in sorted(found):
        print(f"{k} {found[k]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("usage: skill.py doctor|new|test|list ...")
        return 2
    cmd = args[0]
    if cmd == "doctor" and len(args) == 2:
        return cmd_doctor(args[1])
    if cmd == "new" and len(args) == 2:
        return cmd_new(args[1])
    if cmd == "test" and len(args) == 2:
        return cmd_test(args[1])
    if cmd == "list" and len(args) == 1:
        return cmd_list()
    print("usage: skill.py doctor <id> | new <id> | test <id> | list")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
