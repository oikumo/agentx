"""Worktree execution isolation — feature_081.worktree_execution_isolation
(T5-3 2C, mh8 D11 worktree-per-generation, NEXT_STEP §7–§9).

Goldens: claim stamps workspace metadata + bootstraps the dir; two task
worktrees dirty independently while observing one shared coordination state;
a claim never authorizes edits in the integration worktree; stale-generation
workspace cannot publish; transfer moves to a new workspace (old dir kept,
old gen fenced); CLI gate enforces the managed check.

Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT (tmp).
Canary: new goldens for feature_081 only (scope: tests).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))


def _state():
    from net import state  # noqa: PLC0415 (lazy — runnable RED)

    return state


def _workspace():
    from net import workspace  # noqa: PLC0415 (lazy — runnable RED)

    return workspace


def _pool_bundle(base: Path, state, tasks=("T1", "T2")) -> None:
    """Pool net (test_net_task_claim_generation.py shape) + pending bindings."""
    state.init_empty(base)
    st = state.load(base)
    for place, tokens in (
        ("work_pending", len(tasks)),
        ("work_active", 0),
        ("work_done", 0),
        ("agent_attention", 1),
        ("feature_ready", 1),
    ):
        st.net.add_place(place, tokens=tokens)
    st.net.add_transition("work_start")
    st.net.add_transition("work_complete")
    st.net.add_input("agent_attention", "work_start")
    st.net.add_input("feature_ready", "work_start")
    st.net.add_input("work_pending", "work_start")
    st.net.add_output("work_start", "feature_ready")
    st.net.add_output("work_start", "work_active")
    st.net.add_input("work_active", "work_complete")
    st.net.add_output("work_complete", "agent_attention")
    st.net.add_output("work_complete", "work_done")
    st.live_marking = {
        "work_pending": len(tasks),
        "work_active": 0,
        "work_done": 0,
        "agent_attention": 1,
        "feature_ready": 1,
    }
    st.task_bindings = [
        {"id": tid, "place": "work_pending", "generation": 0} for tid in tasks
    ]
    state.save(base, st)


@pytest.fixture()
def bundle(tmp_path, monkeypatch):
    state = _state()
    monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
    monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
    _pool_bundle(tmp_path, state)
    return tmp_path


def _binding(state, base, task_id):
    st = state.load(base)
    return st, next(b for b in st.task_bindings if b["id"] == task_id)


class TestClaimStampsWorkspace:
    def test_claim_records_branch_worktree_base(self, bundle) -> None:
        """T5-3: claim = bootstrap — workspace {id,path,branch,base_commit}."""
        state = _state()
        st = state.claim_task(bundle, "T1", owner="alice", session="coord")
        b = next(x for x in st.task_bindings if x["id"] == "T1")
        ws = b.get("workspace") or {}
        assert ws.get("id") == "T1-g1"
        assert ws.get("branch") == "omt/T1/g1"
        assert str(ws.get("path", "")).endswith(str(Path(".worktrees") / "T1-g1"))
        assert isinstance(ws.get("base_commit"), str) and ws["base_commit"]
        assert b["generation"] == 1
        # the worktree dir is bootstrapped on disk
        assert Path(str(ws["path"])).is_dir()

    def test_two_worktrees_dirty_independently_shared_coordination(
        self, bundle
    ) -> None:
        """T5-3 acceptance: two worktrees dirty independently, one authority."""
        state = _state()
        workspace = _workspace()
        state.claim_task(bundle, "T1", owner="alice", session="coord")
        state.claim_task(bundle, "T2", owner="bob", session="coord")
        st, b1 = _binding(state, bundle, "T1")
        _, b2 = _binding(state, bundle, "T2")
        p1 = Path(str(b1["workspace"]["path"]))
        p2 = Path(str(b2["workspace"]["path"]))
        assert p1 != p2
        (p1 / "draft.txt").write_text("alice work", encoding="utf-8")
        (p2 / "draft.txt").write_text("bob work", encoding="utf-8")
        assert (p1 / "draft.txt").read_text(encoding="utf-8") == "alice work"
        assert (p2 / "draft.txt").read_text(encoding="utf-8") == "bob work"
        # both observe the same authoritative coordination state
        st = state.load(bundle)
        assert st.revision >= 2
        assert workspace.repo_root_for(bundle) == bundle


class TestManagedGate:
    def test_integration_path_refused_workspace_path_allowed(self, bundle) -> None:
        """T5-3 acceptance: a claim cannot authorize the integration tree."""
        state = _state()
        state.claim_task(bundle, "T1", owner="alice", session="coord")
        _, b = _binding(state, bundle, "T1")
        ws_path = str(b["workspace"]["path"])
        ok = state.check_workspace_edit(
            bundle, "T1", generation=1, path=str(Path(ws_path) / "src" / "x.py"), owner="alice"
        )
        assert ok["generation"] == 1
        with pytest.raises(state.SpliceError) as exc:
            state.check_workspace_edit(
                bundle, "T1", generation=1, path=str(bundle / "src" / "x.py"), owner="alice"
            )
        assert exc.value.code == "workspace_mismatch"

    def test_wrong_owner_and_stale_gen_refused(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "T1", owner="alice", session="coord")
        _, b = _binding(state, bundle, "T1")
        ws_path = str(b["workspace"]["path"])
        with pytest.raises(state.SpliceError) as exc:
            state.check_workspace_edit(
                bundle, "T1", generation=1, path=str(Path(ws_path) / "f.py"), owner="mallory"
            )
        assert exc.value.code == "not_owner"
        with pytest.raises(state.SpliceError) as exc:
            state.check_workspace_edit(
                bundle, "T1", generation=99, path=str(Path(ws_path) / "f.py"), owner="alice"
            )
        assert exc.value.code == "stale_generation"


class TestStaleWorkspaceCannotPublish:
    def test_transfer_new_workspace_old_gen_fenced(self, bundle) -> None:
        """D11: one branch/worktree per generation; stale cannot publish."""
        state = _state()
        state.claim_task(bundle, "T1", owner="alice", session="coord")
        _, old = _binding(state, bundle, "T1")
        old_path = Path(str(old["workspace"]["path"]))
        state.transfer_task(bundle, "T1", owner="bob", session="coord")
        _, new = _binding(state, bundle, "T1")
        assert new["generation"] == 2
        assert new["workspace"]["id"] == "T1-g2"
        assert new["workspace"]["path"] != old["workspace"]["path"]
        assert Path(str(new["workspace"]["path"])).is_dir()
        assert old_path.is_dir()  # stale workspace survives, cannot publish
        with pytest.raises(state.SpliceError) as exc:
            state.checkpoint_task(bundle, "T1", generation=1, checkpoint="stale")
        assert exc.value.code == "stale_generation"

    def test_checkpoint_records_head_and_patch_digest(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "T1", owner="alice", session="coord")
        state.checkpoint_task(
            bundle,
            "T1",
            generation=1,
            checkpoint="green",
            head_commit="def456",
            patch_digest="sha256:abc",
        )
        _, b = _binding(state, bundle, "T1")
        assert b["workspace"].get("head_commit") == "def456"
        assert b["workspace"].get("patch_digest") == "sha256:abc"


class TestCliGateManaged:
    def test_gate_task_scoped_allow_and_refuse(self, bundle, capsys) -> None:
        """CLI `gate --task-id --generation` mirrors the managed check."""
        from net import cli  # noqa: PLC0415 (lazy — runnable RED)

        state = _state()
        state.claim_task(bundle, "T1", owner="alice", session="coord")
        _, b = _binding(state, bundle, "T1")
        ws_path = str(b["workspace"]["path"])
        rc = cli.main(
            [
                "gate",
                "--path",
                str(Path(ws_path) / "src" / "x.py"),
                "--task-id",
                "T1",
                "--generation",
                "1",
                "--owner",
                "alice",
                "--session",
                "coord",
            ]
        )
        assert rc == 0
        rc = cli.main(
            [
                "gate",
                "--path",
                str(bundle / "src" / "x.py"),
                "--task-id",
                "T1",
                "--generation",
                "1",
                "--owner",
                "alice",
                "--session",
                "coord",
            ]
        )
        assert rc == 1
        _ = capsys.readouterr()
