"""Agent demo subsystem — self-contained demo scenarios for feature_007.

This package holds the seeded *data* (goals, policy rules, sandbox files) used by
demo scenarios (feature_010) to demonstrate the intelligent-agent
cycle with a single trigger.  It lives in the Model layer: it contains no UI
code and no controller imports — the :class:`AgentController` translates these
lightweight specs into real :class:`Goal` / :class:`PolicyRule` objects.

Triad map::

    agent/demo/scenarios.py   Model/data — DemoScenario A/B + seed_sandbox_files()
    agent/controller/         Controller — load_demo_scenario_by_name()
    agent/view/agent_view.py  View — console agent view
"""
