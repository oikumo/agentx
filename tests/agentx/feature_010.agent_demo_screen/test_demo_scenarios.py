"""Unit tests for the demo scenario data module (feature_010)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentx.agent.demo.scenarios import (
    SCENARIO_A,
    SCENARIO_B,
    DemoScenario,
    get_scenario,
    list_scenarios,
    seed_sandbox_files,
)


class TestScenarioRegistry:
    def test_two_scenarios_registered(self):
        scenarios = list_scenarios()
        assert len(scenarios) == 2
        assert {s.key for s in scenarios} == {"a", "b"}

    def test_get_scenario_case_insensitive(self):
        assert get_scenario("a") is SCENARIO_A
        assert get_scenario("B") is SCENARIO_B
        assert get_scenario("  a ") is SCENARIO_A

    def test_get_scenario_unknown_returns_none(self):
        assert get_scenario("z") is None
        assert get_scenario("") is None
        assert get_scenario(None) is None  # type: ignore[arg-type]


class TestScenarioA:
    def test_shape(self):
        assert SCENARIO_A.key == "a"
        assert SCENARIO_A.name == "File Reader Agent"
        assert SCENARIO_A.goal.description
        assert SCENARIO_A.goal.success_kind == "tool_success"
        assert SCENARIO_A.goal.success_tool_id == "filesystem"
        assert len(SCENARIO_A.rules) == 1
        rule = SCENARIO_A.rules[0]
        assert rule.condition_expr == "goal.active"
        assert rule.parameters["tool_id"] == "filesystem"
        assert rule.parameters["action"] == "read"
        assert "target.txt" in SCENARIO_A.files


class TestScenarioB:
    def test_shape(self):
        assert SCENARIO_B.key == "b"
        assert SCENARIO_B.name == "Knowledge Assistant"
        assert len(SCENARIO_B.rules) == 2
        # rule 1: read notes when goal active
        r1 = SCENARIO_B.rules[0]
        assert r1.condition_expr == "goal.active"
        assert r1.parameters["action"] == "read"
        assert r1.parameters["path"] == "notes.txt"
        # rule 2: create summary when memory has notes but not summary
        r2 = SCENARIO_B.rules[1]
        assert "memory_contains" in r2.condition_expr
        assert "NOT" in r2.condition_expr
        assert r2.parameters["action"] == "create"
        assert r2.parameters["path"] == "summary.txt"
        assert "notes.txt" in SCENARIO_B.files


class TestSeedSandboxFiles:
    def test_writes_files(self, sandbox_dir):
        written = seed_sandbox_files(SCENARIO_A, sandbox_dir)
        assert written == ["target.txt"]
        assert (Path(sandbox_dir) / "target.txt").is_file()
        content = (Path(sandbox_dir) / "target.txt").read_text()
        assert "agent" in content.lower()

    def test_idempotent_overwrite(self, sandbox_dir):
        seed_sandbox_files(SCENARIO_A, sandbox_dir)
        # write again — should overwrite, not error
        seed_sandbox_files(SCENARIO_A, sandbox_dir)
        assert (Path(sandbox_dir) / "target.txt").is_file()

    def test_creates_parent_dirs(self, sandbox_dir):
        scenario = DemoScenario(
            key="x",
            name="Nested",
            description="d",
            goal=SCENARIO_A.goal,
            rules=[],
            files={"sub/dir/file.txt": "nested content"},
        )
        written = seed_sandbox_files(scenario, sandbox_dir)
        assert "sub/dir/file.txt" in written
        assert (Path(sandbox_dir) / "sub" / "dir" / "file.txt").is_file()

    def test_rejects_path_escape(self, sandbox_dir):
        scenario = DemoScenario(
            key="x",
            name="Escape",
            description="d",
            goal=SCENARIO_A.goal,
            rules=[],
            files={"../escape.txt": "bad"},
        )
        with pytest.raises(ValueError):
            seed_sandbox_files(scenario, sandbox_dir)

    def test_scenario_b_files(self, sandbox_dir):
        written = seed_sandbox_files(SCENARIO_B, sandbox_dir)
        assert written == ["notes.txt"]
        notes = (Path(sandbox_dir) / "notes.txt").read_text()
        assert "Project Notes" in notes
