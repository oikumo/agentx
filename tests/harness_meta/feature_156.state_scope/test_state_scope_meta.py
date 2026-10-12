"""StateScope goldens (feature_156) — ownership doc pins stateless skills."""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCOPE_DOC = REPO / ".meta" / "templates" / "state.scope.md"
SKILLS_DIRS = [REPO / ".opencode" / "skills", REPO / ".agents" / "skills"]


class TestStateScope:
    def test_scope_doc_lists_five_owners(self):
        text = SCOPE_DOC.read_text(encoding="utf-8")
        for scope in ("invocation", "session", "feature", "project", "harness"):
            assert scope in text.lower(), scope
        assert "skills own nothing" in text.lower().replace("  ", " ") or "own nothing" in text.lower()

    def test_skills_own_no_state_files(self):
        strays = []
        for base in SKILLS_DIRS:
            if not base.exists():
                continue
            for p in base.rglob(".skill-state.json"):
                strays.append(str(p))
        assert strays == [], strays

    def test_contracts_pin_state_owner_external(self):
        for base in SKILLS_DIRS:
            if not base.exists():
                continue
            for contract in base.glob("*/skill.contract.json"):
                data = json.loads(contract.read_text(encoding="utf-8"))
                assert data.get("state_owner") == "external", contract
