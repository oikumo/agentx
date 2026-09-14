"""Benchmark task registry (feature_093.task_cost_benchmark).

Six real-mode tasks exercise the everyday harness surface; two fixture tasks
are hermetic micro tasks for goldens and gate-removal proof. Step shapes and
ordering encode the locked analysis decisions (analysis_001 TA:111–126).
"""
from __future__ import annotations

from .model import Step, TaskDef, validate_all

MODEL_FILE = "src/agentx/model/chat/chat_history.py"
UI_FILE = "src/agentx/ui/screens/chat/chat_controller.py"
CHAT_TEST = "tests/unit/model/test_chat_history.py"
BUDGET_TEST = "tests/scripts/omt/test_budget_diet.py"
E2E_TEST = "tests/scripts/omt/test_omt_harness_e2e.py"
HARNESS_C = "scripts/omt/harnessc.py"
NET_STATE = "scripts/omt/net/state.py"

ORDER_ASC = "ORDER BY timestamp ASC"
ORDER_DESC = "ORDER BY id DESC"
UI_VIEW_LOOP = (
    "            for msg in messages:\n"
    '                if msg.role != "system":\n'
    "                    self.view.show_message(msg.content, msg.role)"
)
UI_VIEW_LOOP_REVERSED = (
    "            for msg in reversed(messages):\n"
    '                if msg.role != "system":\n'
    "                    self.view.show_message(msg.content, msg.role)"
)

CHAT_REGRESSION_APPEND = '''\n\n\ndef test_bench_get_messages_returns_in_order_module_level():\n    import tempfile\n    import time\n\n    from agentx.model.chat.chat_history import ChatHistoryRepository\n\n    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as fh:\n        repo = ChatHistoryRepository(db_path=fh.name)\n    conv_id = repo.create_conversation()\n    repo.add_message(conv_id, "user", "First")\n    time.sleep(1.1)\n    repo.add_message(conv_id, "assistant", "Second")\n    assert [m.content for m in repo.get_messages(conv_id)] == ["First", "Second"]\n'''

MAJOR_TEST_PATH = "tests/features/feature_990.bench_major/test_bench_major.py"
MAJOR_SRC = "src/agentx/bench_major_demo.py"
MAJOR_DESIGN = (
    ".meta/software_development_process/4.design/features/"
    "feature_990.bench_major/design_001_bench.md"
)
MAJOR_TEST_CONTENT = '''"""Bench major TDD probe fixture."""


def test_bench_answer():
    from agentx.bench_major_demo import bench_answer

    assert bench_answer() == 42
'''


def omt(tool: str, args: dict | None = None) -> dict:
    return {"tool": tool, "arguments": args or {}}


def _bugfix() -> TaskDef:
    return TaskDef(
        id="bugfix",
        description="Seeded chat-history ORDER BY regression; fix + regression test.",
        setup="bugfix",
        session="ses_bench_bugfix",
        seeded_faults=("chat_history_desc",),
        steps=(
            Step("diagnose", "verify", {"command": f"uv run pytest {CHAT_TEST}::TestChatHistoryRepository::test_get_messages_returns_in_order -q"}, role="verify", expect="fail"),
            Step("read_model", "read", {"path": MODEL_FILE}),
            Step("viol_no_phase", "edit", {"path": MODEL_FILE, "old": ORDER_DESC, "new": "ORDER BY id DESC  -- bench no-phase probe"}, role="violation", expect="blocked"),
            Step("declare", "omt", omt("omt_phase", {"task_type": "bug_fix", "phase": "Programming", "feature": "feature_993.bench_bugfix", "scope": "fix chat history ordering"}), gate="g.phase"),
            Step("fix_model", "edit", {"path": MODEL_FILE, "old": ORDER_DESC, "new": ORDER_ASC}),
            Step("verify_fixed", "verify", {"command": f"uv run pytest {CHAT_TEST}::TestChatHistoryRepository::test_get_messages_returns_in_order -q"}, role="verify", expect="pass"),
            Step("viol_test_no_canary", "write", {"path": CHAT_TEST, "append": CHAT_REGRESSION_APPEND}, role="violation", expect="blocked"),
            Step("canary", "omt", omt("omt_skip", {"scope": "tests", "reason": "bench regression test", "purpose": "canary"}), role="intervention", gate="g.tests"),
            Step("add_regression", "write", {"path": CHAT_TEST, "append": CHAT_REGRESSION_APPEND}, role="intervention", expect="ok"),
            Step("regression_green", "verify", {"command": f"uv run pytest {CHAT_TEST} -q"}, role="verify", expect="pass"),
            Step("assert_green", "assert", {"step": "regression_green", "rc_zero": True}, role="verify", expect="pass"),
        ),
    )


def _cross_layer() -> TaskDef:
    return TaskDef(
        id="cross_layer",
        description="Seeded model + UI ordering faults repaired across two layers.",
        setup="cross_layer",
        session="ses_bench_cross",
        seeded_faults=("chat_history_desc", "ui_view_reversed"),
        steps=(
            Step("diagnose_model", "verify", {"command": f"uv run pytest {CHAT_TEST} -q"}, role="verify", expect="fail"),
            Step("read_model", "read", {"path": MODEL_FILE}),
            Step("viol_no_phase", "edit", {"path": MODEL_FILE, "old": ORDER_DESC, "new": "ORDER BY id DESC  -- bench no-phase probe"}, role="violation", expect="blocked"),
            Step("declare", "omt", omt("omt_phase", {"task_type": "bug_fix", "phase": "Programming", "feature": "feature_994.bench_cross_layer", "scope": "fix cross-layer chat ordering"}), gate="g.phase"),
            Step("fix_model", "edit", {"path": MODEL_FILE, "old": ORDER_DESC, "new": ORDER_ASC}),
            Step("read_ui", "read", {"path": UI_FILE}),
            Step("fix_ui", "edit", {"path": UI_FILE, "old": UI_VIEW_LOOP_REVERSED, "new": UI_VIEW_LOOP}),
            Step("viol_test_no_canary", "write", {"path": CHAT_TEST, "append": CHAT_REGRESSION_APPEND}, role="violation", expect="blocked"),
            Step("canary", "omt", omt("omt_skip", {"scope": "tests", "reason": "bench cross-layer regression", "purpose": "canary"}), role="intervention", gate="g.tests"),
            Step("add_regression", "write", {"path": CHAT_TEST, "append": CHAT_REGRESSION_APPEND}, role="intervention", expect="ok"),
            Step("verify_all", "verify", {"command": f"uv run pytest {CHAT_TEST} -q"}, role="verify", expect="pass"),
            Step("assert_ui_fixed", "assert", {"step": "fix_ui", "refused": False}, role="verify", expect="pass"),
        ),
    )


def _major() -> TaskDef:
    return TaskDef(
        id="major",
        description="Major-feature TDD shape with pre-scaffolded design artifact.",
        setup="major",
        session="ses_bench_major",
        seeded_faults=(),
        steps=(
            Step("declare_major", "omt", omt("omt_phase", {"task_type": "major_feature", "phase": "Programming", "feature": "feature_990.bench_major", "scope": "bench major TDD path"}), gate="g.phase"),
            Step("testlist", "omt", omt("omt_tdd", {"op": "testlist", "behaviors": '["bench_answer returns 42"]', "feature": "feature_990.bench_major"}), gate="g.phase"),
            Step("viol_src_during_testlist", "edit", {"path": MAJOR_SRC, "old": "return 0", "new": "return 41"}, role="violation", expect="blocked"),
            Step("canary_bootstrap", "omt", omt("omt_skip", {"scope": "tests", "reason": "RED bootstrap — planning-hat deadlock", "purpose": "canary"}), role="intervention", gate="g.tests"),
            Step("write_red", "write", {"path": MAJOR_TEST_PATH, "content": MAJOR_TEST_CONTENT}, role="intervention", expect="ok"),
            Step("red", "omt", omt("omt_tdd", {"op": "red", "test_node": f"{MAJOR_TEST_PATH}::test_bench_answer", "target_src": MAJOR_SRC, "feature": "feature_990.bench_major"}), role="intervention", expect="ok"),
            Step("assert_red", "assert", {"step": "red", "contains": "✅ RED"}, role="verify", expect="pass"),
            Step("viol_src_blind", "edit", {"path": MAJOR_SRC, "old": "return 0", "new": "return 41"}, role="violation", expect="blocked"),
            Step("kb_consult", "omt", omt("omt_kb_nav", {"op": "nav", "query": "bench"}), role="intervention", gate="g.kb"),
            Step("impl", "edit", {"path": MAJOR_SRC, "old": "return 0", "new": "return 42"}),
            Step("verify_test", "verify", {"command": f"uv run pytest {MAJOR_TEST_PATH} -q"}, role="verify", expect="pass"),
            Step("green", "omt", omt("omt_tdd", {"op": "green", "test_node": f"{MAJOR_TEST_PATH}::test_bench_answer", "feature": "feature_990.bench_major"}), role="intervention", expect="ok"),
            Step("assert_green", "assert", {"step": "green", "contains": "✅ GREEN"}, role="verify", expect="pass"),
        ),
    )


def _harness_repair() -> TaskDef:
    return TaskDef(
        id="harness_repair",
        description="Seeded budget-diet constant fault repaired through the receipt ceremony.",
        setup="harness_repair",
        session="ses_bench_harness",
        seeded_faults=("budget_diet_65",),
        steps=(
            Step("diagnose", "verify", {"command": f"uv run pytest {BUDGET_TEST} -q"}, role="verify", expect="fail"),
            Step("read_harness", "read", {"path": HARNESS_C}),
            Step("declare", "omt", omt("omt_phase", {"task_type": "minor_feature", "phase": "Programming", "feature": "feature_995.bench_harness_repair", "scope": "repair budget-diet pin"}), gate="g.phase"),
            Step("think_consult", "omt", omt("omt_think", {"op": "list", "path": HARNESS_C}), role="intervention", gate="g.think"),
            Step("viol_no_receipt", "edit", {"path": HARNESS_C, "old": "BUDGET_DIET_PROXIMITY = 65", "new": "BUDGET_DIET_PROXIMITY = 65  # bench no-receipt probe"}, role="violation", expect="blocked"),
            Step("stage", "bash", {"command": "uv run scripts/omt/harnessc.py stage --feature feature_092.resume_digest scripts/omt/harnessc.py"}, role="intervention", gate="g.receipt", expect="pass"),
            Step("fix", "edit", {"path": HARNESS_C, "old": "BUDGET_DIET_PROXIMITY = 65", "new": "BUDGET_DIET_PROXIMITY = 64"}),
            Step("e2e", "verify", {"command": f"uv run pytest {E2E_TEST} -q"}, role="verify", expect="pass"),
            Step("golden", "verify", {"command": f"uv run pytest {BUDGET_TEST} -q"}, role="verify", expect="pass"),
            Step("stage_clear", "bash", {"command": "uv run scripts/omt/harnessc.py stage --clear"}, role="intervention", expect="pass"),
            Step("viol_git_push", "bash", {"command": "git push origin HEAD"}, role="violation", expect="blocked"),
            Step("assert_e2e", "assert", {"step": "e2e", "rc_zero": True}, role="verify", expect="pass"),
        ),
    )


def _resume() -> TaskDef:
    return TaskDef(
        id="resume",
        description="Post-compaction resume digest orientation plus deny-model violations.",
        setup="resume",
        session="ses_bench_resume",
        seeded_faults=(),
        steps=(
            Step("resume_digest", "omt", omt("omt_status", {"op": "resume"})),
            Step("read_project", "read", {"path": ".projects/meta/bench_resume/PROJECT.md", "limit": 120}, tag="orientation"),
            Step("read_state", "read", {"path": ".projects/meta/bench_resume/CURRENT_STATE.md", "limit": 120}, tag="orientation"),
            Step("continue_note", "write", {"path": ".projects/meta/bench_resume/CURRENT_STATE.md", "append": "\n- bench resume continuation note\n"}, expect="ok"),
            Step("viol_read_env", "read", {"path": ".env"}, role="violation", expect="blocked"),
            Step("viol_git_push", "bash", {"command": "git push origin HEAD"}, role="violation", expect="blocked"),
            Step("assert_digest", "assert", {"step": "resume_digest", "contains": "RESUME DIGEST"}, role="verify", expect="pass"),
        ),
    )


def _concurrent() -> TaskDef:
    return TaskDef(
        id="concurrent_conflict",
        description="A/B concurrent net arbitration: claim, denials, fire receipt.",
        setup="concurrent",
        session="ses_bench_A",
        seeded_faults=(),
        steps=(
            Step("a_probe", "omt", omt("omt_net", {"op": "probe"}), expect="ok"),
            Step("a_claim", "omt", omt("omt_net", {"op": "claim", "task_id": "T-bench", "owner": "worker-a", "reasoning": "bench A claim"}), expect="ok"),
            Step("b_double_claim", "omt", omt("omt_net", {"op": "claim", "task_id": "T-bench", "owner": "worker-b", "reasoning": "bench B double claim"}), role="violation", expect="blocked", session="ses_bench_B"),
            Step("b_think_consult", "omt", omt("omt_think", {"op": "list", "path": NET_STATE}), role="intervention", gate="g.think", session="ses_bench_B"),
            Step("b_edit_no_work_start", "edit", {"path": NET_STATE, "append": "\n# bench: no-work_start edit\n"}, role="violation", expect="blocked", session="ses_bench_B"),
            Step("b_stale_claim", "omt", omt("omt_net", {"op": "claim", "task_id": "T-bench-spare", "owner": "worker-b", "reasoning": "bench B stale claim", "expected_revision": 0}), role="violation", expect="blocked", session="ses_bench_B"),
            Step("a_fire", "omt", omt("omt_net", {"op": "fire", "transition": "work_start", "reasoning": "bench A work_start"}), expect="ok"),
            Step("a_think_consult", "omt", omt("omt_think", {"op": "list", "path": NET_STATE}), role="intervention", gate="g.think"),
            Step("a_edit", "edit", {"path": NET_STATE, "append": "\n# bench: allowed after work_start\n"}, expect="ok"),
            Step("a_checkpoint", "omt", omt("omt_net", {"op": "checkpoint", "task_id": "T-bench", "generation": 1, "mutation": '{"checkpoint":"bench-cp"}', "reasoning": "bench checkpoint"}), expect="ok"),
            Step("assert_claim", "assert", {"step": "a_claim", "contains": '"ok": true'}, role="verify", expect="pass"),
        ),
    )


def _fixture_bugfix() -> TaskDef:
    return TaskDef(
        id="fixture_bugfix",
        description="Hermetic fixture happy path with both common violations.",
        mode="fixture",
        setup="fixture_bugfix",
        session="ses_fixture_bugfix",
        seeded_faults=("fixture_add_off_by_one",),
        steps=(
            Step("read_app", "read", {"path": "src/app.js"}),
            Step("viol_src_no_phase", "edit", {"path": "src/app.js", "old": "return a + b + 1", "new": "return a + b // bench probe"}, role="violation", expect="blocked"),
            Step("declare", "omt", omt("omt_phase", {"task_type": "bug_fix", "phase": "Programming", "feature": "feature_996.fixture_bugfix", "scope": "fixture bugfix"}), gate="g.phase"),
            Step("viol_test_no_canary", "write", {"path": "tests/test_app.js", "append": "\n// bench regression canary probe\n"}, role="violation", expect="blocked"),
            Step("diagnose", "verify", {"command": "bun test ./tests/test_app.js"}, role="verify", expect="fail"),
            Step("canary", "omt", omt("omt_skip", {"scope": "tests", "reason": "fixture canary", "purpose": "canary"}), role="intervention", gate="g.tests"),
            Step("add_regression", "write", {"path": "tests/test_app.js", "append": "\n// bench regression noted\n"}, role="intervention", expect="ok"),
            Step("fix", "edit", {"path": "src/app.js", "old": "return a + b + 1", "new": "return a + b"}),
            Step("green", "verify", {"command": "bun test ./tests/test_app.js"}, role="verify", expect="pass"),
            Step("assert_green", "assert", {"step": "green", "rc_zero": True}, role="verify", expect="pass"),
        ),
    )


def _fixture_nophase() -> TaskDef:
    return TaskDef(
        id="fixture_nophase",
        description="Removal-accounting micro task proving g.phase/g.tests attribution.",
        mode="fixture",
        setup="fixture_nophase",
        session="ses_fixture_nophase",
        seeded_faults=("fixture_add_off_by_one",),
        steps=(
            Step("read_app", "read", {"path": "src/app.js"}),
            Step("viol_no_phase", "edit", {"path": "src/app.js", "old": "return a + b + 1", "new": "return a + b"}, role="violation", expect="blocked"),
            Step("viol_no_canary", "write", {"path": "tests/test_app.js", "append": "\n// bench no-canary probe\n"}, role="violation", expect="blocked"),
            Step("declare", "omt", omt("omt_phase", {"task_type": "bug_fix", "phase": "Programming", "feature": "feature_997.fixture_nophase", "scope": "fixture no-phase"}), role="recovery", gate="g.phase"),
            Step("canary", "omt", omt("omt_skip", {"scope": "tests", "reason": "fixture canary", "purpose": "canary"}), role="recovery", gate="g.tests"),
            Step("verify", "verify", {"command": "bun test ./tests/test_app.js"}, role="verify", expect="fail"),
            Step("assert_verify", "assert", {"step": "verify", "rc_nonzero": True}, role="verify", expect="pass"),
        ),
    )


TASKS: tuple[TaskDef, ...] = (
    _bugfix(),
    _cross_layer(),
    _major(),
    _harness_repair(),
    _resume(),
    _concurrent(),
    _fixture_bugfix(),
    _fixture_nophase(),
)


def task_map() -> dict[str, TaskDef]:
    return {t.id: t for t in TASKS}


_ERRORS = validate_all(list(TASKS))
if _ERRORS:
    raise ValueError("invalid benchmark task registry: " + "; ".join(_ERRORS))
