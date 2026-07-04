"""Unit tests for demo controller + model clear operations (feature_010)."""

from __future__ import annotations

from pathlib import Path

from agentx.agent.types import GoalStatus


# ---------------------------------------------------------------------------
# Model layer: clear operations
# ---------------------------------------------------------------------------


class TestGoalManagerClear:
    def test_clear_empties_tree(self, wired_controller):
        agent, controller = wired_controller
        controller.submit_goal("a goal")
        assert len(controller.list_goals().nodes) == 1
        agent.goal_manager.clear()
        tree = agent.goal_manager.get_tree()
        assert tree.nodes == {}
        assert tree.root is None

    def test_clear_is_idempotent(self, wired_controller):
        agent, _ = wired_controller
        agent.goal_manager.clear()
        agent.goal_manager.clear()  # no error
        assert agent.goal_manager.get_tree().nodes == {}


class TestMemoryManagerClearVolatile:
    def test_clear_empties_volatile(self, wired_controller):
        agent, _ = wired_controller
        # run a cycle to populate memory via perception
        controller = wired_controller[1]
        controller.submit_goal("g")
        agent.run_cycle()
        assert agent.memory.count_volatile() > 0
        agent.memory.clear_volatile()
        assert agent.memory.count_volatile() == 0


class TestAgentClearState:
    def test_clears_all_subsystems(self, wired_controller):
        agent, controller = wired_controller
        controller.submit_goal("g1")
        controller.submit_goal("g2")
        agent.clear_state()
        assert len(controller.list_goals().nodes) == 0
        assert len(controller.list_rules()) == 0
        assert agent.memory.count_volatile() == 0

    def test_resets_state_to_perceiving(self, wired_controller):
        agent, _ = wired_controller
        agent.state = agent.state.TERMINATED  # type: ignore[attr-defined]
        agent.clear_state()
        assert agent.state.value == "PERCEIVING"


# ---------------------------------------------------------------------------
# Controller layer: reset_state + load_demo_scenario_by_name
# ---------------------------------------------------------------------------


class TestResetState:
    def test_clears_via_controller(self, wired_controller):
        agent, controller = wired_controller
        controller.submit_goal("g")
        assert len(controller.list_goals().nodes) == 1
        controller.reset_state()
        assert len(controller.list_goals().nodes) == 0
        assert agent.memory.count_volatile() == 0


class TestLoadDemoScenarioByName:
    def test_load_scenario_a(self, wired_controller):
        agent, controller = wired_controller
        ok = controller.load_demo_scenario_by_name("a")
        assert ok is True
        goals = controller.list_goals()
        assert len(goals.nodes) == 1
        assert len(controller.list_rules()) == 1
        # sandbox file seeded
        assert (Path(agent.config.sandbox_root) / "target.txt").exists()

    def test_load_scenario_b(self, wired_controller):
        agent, controller = wired_controller
        ok = controller.load_demo_scenario_by_name("B")
        assert ok is True
        assert len(controller.list_goals().nodes) == 1
        assert len(controller.list_rules()) == 2
        assert (Path(agent.config.sandbox_root) / "notes.txt").exists()

    def test_unknown_scenario_returns_false(self, wired_controller):
        _, controller = wired_controller
        ok = controller.load_demo_scenario_by_name("zzz")
        assert ok is False

    def test_load_clears_prior_state_first(self, wired_controller):
        agent, controller = wired_controller
        # pre-populate with manual goal + run a cycle (memory)
        controller.submit_goal("pre-existing manual goal")
        controller.run_cycle()
        assert len(controller.list_goals().nodes) >= 1
        assert agent.memory.count_volatile() > 0
        # loading a scenario must clear first
        controller.load_demo_scenario_by_name("a")
        goals = controller.list_goals()
        # only the scenario goal remains — the manual one is gone
        descriptions = [g.description for g in goals.nodes.values()]
        assert all("manual goal" not in d for d in descriptions)
        assert len(goals.nodes) == 1

    def test_scenario_a_completes_in_one_cycle(self, wired_controller):
        """Scenario A's goal should complete after one filesystem read cycle."""
        agent, controller = wired_controller
        controller.load_demo_scenario_by_name("a")
        result = controller.run_cycle()
        assert result.action_result is not None
        assert result.action_result.success is True
        goals = list(controller.list_goals().nodes.values())
        assert goals[0].status == GoalStatus.COMPLETED

    def test_scenario_b_two_cycle_flow(self, wired_controller):
        """Scenario B: cycle1 reads notes (goal completes), cycle2 creates summary."""
        agent, controller = wired_controller
        controller.load_demo_scenario_by_name("b")
        # cycle 1 — read notes
        r1 = controller.run_cycle()
        assert r1.action_result.success is True
        assert r1.action_result.output.get("path") == "notes.txt"
        # cycle 2 — create summary (memory-driven)
        r2 = controller.run_cycle()
        assert r2.action_result.success is True
        assert (Path(agent.config.sandbox_root) / "summary.txt").exists()
        # cycle 3 — idle (summary exists, rule 2 condition false)
        r3 = controller.run_cycle()
        # no create repeats; summary content stable
        content = (Path(agent.config.sandbox_root) / "summary.txt").read_text()
        assert "Summary" in content

    def test_reset_reseeds_scenario(self, wired_controller):
        """Calling load again (reset) clears and re-seeds idempotently."""
        agent, controller = wired_controller
        controller.load_demo_scenario_by_name("a")
        controller.run_cycle()  # goal completes, memory grows
        assert agent.memory.count_volatile() > 0
        # re-seed (reset)
        ok = controller.load_demo_scenario_by_name("a")
        assert ok is True
        # state cleared + re-seeded: one goal, PENDING/ACTIVE, memory empty
        assert len(controller.list_goals().nodes) == 1
        assert agent.memory.count_volatile() == 0


class TestGetDemoScenarioInfo:
    def test_returns_display_info(self, wired_controller):
        _, controller = wired_controller
        info = controller.get_demo_scenario_info("a")
        assert info is not None
        assert info["key"] == "a"
        assert info["name"] == "File Reader Agent"
        assert "description" in info
        assert "target.txt" in info["files"]

    def test_unknown_returns_none(self, wired_controller):
        _, controller = wired_controller
        assert controller.get_demo_scenario_info("nope") is None
