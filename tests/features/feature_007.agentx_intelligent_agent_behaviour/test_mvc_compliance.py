"""MVC++ compliance tests — verify mvc_check.py reports 0 errors on agent module (T3)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]


class TestMvcCompliance:
    def test_agent_module_zero_errors(self):
        """mvc_check.py must report 0 errors on src/agentx/agent/."""
        result = subprocess.run(
            ["uv", "run", "scripts/omt/mvc_check.py", "src/agentx/agent/", "--json"],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
        )
        assert result.returncode == 0, f"mvc_check failed: {result.stderr}"
        data = json.loads(result.stdout)
        assert data["errors"] == 0, (
            f"MVC++ violations found: {data['errors']} errors\n"
            + json.dumps(data["findings"], indent=2)
        )

    def test_agent_module_warnings_acceptable(self):
        """mvc_check.py should report 0 warnings on src/agentx/agent/."""
        result = subprocess.run(
            ["uv", "run", "scripts/omt/mvc_check.py", "src/agentx/agent/", "--json"],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
        )
        data = json.loads(result.stdout)
        agent_warnings = [
            f for f in data["findings"]
            if "src/agentx/agent/" in f["file"]
        ]
        assert len(agent_warnings) == 0, (
            f"Unexpected warnings in agent module: {agent_warnings}"
        )

    def test_no_view_imports_model(self):
        """No view file under agent/ should import from agentx.agent.model."""
        agent_dir = _REPO_ROOT / "src" / "agentx" / "agent"
        view_files = list((agent_dir / "view").rglob("*.py"))
        for vf in view_files:
            source = vf.read_text()
            # View files may import from agentx.agent.interfaces (ABCs) but not model
            assert "from agentx.agent.model" not in source, (
                f"View file {vf.name} imports Model layer — MVC++ violation"
            )

    def test_no_sql_in_controllers(self):
        """No controller file should contain SQL or .execute() calls."""
        agent_dir = _REPO_ROOT / "src" / "agentx" / "agent"
        controller_files = list((agent_dir / "controller").rglob("*.py"))
        for cf in controller_files:
            if cf.name == "__init__.py":
                continue
            source = cf.read_text()
            for i, line in enumerate(source.splitlines(), 1):
                stripped = line.split("#")[0]
                assert ".execute(" not in stripped, (
                    f"SQL in controller {cf.name}:{i} — must be in *_db.py"
                )
                assert "CREATE TABLE" not in stripped.upper(), (
                    f"DDL in controller {cf.name}:{i} — must be in *_db.py"
                )

    def test_all_partners_are_abc(self):
        """All I*Partner classes must inherit from ABC."""
        import inspect

        from agentx.agent import interfaces

        for name, obj in inspect.getmembers(interfaces, inspect.isclass):
            if name.startswith("I") and name.endswith("Partner"):
                from abc import ABC

                assert issubclass(obj, ABC), f"{name} is not an ABC subclass"

    def test_controllers_under_300_loc(self):
        """No controller should exceed 300 lines (god controller check)."""
        agent_dir = _REPO_ROOT / "src" / "agentx" / "agent"
        controller_files = list((agent_dir / "controller").rglob("*_controller.py"))
        for cf in controller_files:
            loc = len(cf.read_text().splitlines())
            assert loc < 300, f"{cf.name} is {loc} loc — exceeds 300 loc god-controller limit"
