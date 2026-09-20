"""B worktree lifecycle goldens - feature_118.mh11_worktree_lifecycle.

Pure composer (resolve_lane / compose_join / gate_complete) plus thin git
boundary (status_checks). Hermetic: tmp git repos only, live rev 60 untouched.
Target imports stay lazy inside tests so a missing module fails as test
failures (exit 1), never collection errors (exit 2).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))


def _lifecycle():
    from net import worktree_lifecycle  # noqa: PLC0415
    return worktree_lifecycle


class TestResolveLane:
    def test_session_lane_roots_under_bench_with_feat_prefix(self):
        lc = _lifecycle()
        got = lc.resolve_lane(task_id="T1", generation=3, lane="general")
        assert got["root"] == ".sandbox/bench"
        assert got["branch"] == "feat/T1-g3"
        assert got["path"] == ".sandbox/bench/T1-g3"

    def test_managed_lane_keeps_081_conventions(self):
        lc = _lifecycle()
        got = lc.resolve_lane(task_id="T17", generation=3, lane="managed")
        assert got["root"] == ".worktrees"
        assert got["branch"] == "omt/T17/g3"

    def test_refuses_empty_task_and_bad_generation(self):
        lc = _lifecycle()
        with pytest.raises(lc.LifecycleRefused):
            lc.resolve_lane(task_id="", generation=0)
        with pytest.raises(lc.LifecycleRefused):
            lc.resolve_lane(task_id="T1", generation=-1)


class TestComposeJoin:
    def test_noff_merge_ordered_with_cleanup(self):
        lc = _lifecycle()
        tasks = [
            {"task_id": "T2", "path": ".sandbox/bench/T2-g0",
             "branch": "feat/T2-g0", "head": "aaa"},
            {"task_id": "T1", "path": ".sandbox/bench/T1-g0",
             "branch": "feat/T1-g0", "head": "bbb"},
        ]
        got = lc.compose_join(tasks=tasks)
        cmds = got["commands"]
        assert cmds[0] == "git merge --no-ff feat/T1-g0"
        assert cmds[1] == "git merge --no-ff feat/T2-g0"
        assert "git worktree remove --force .sandbox/bench/T1-g0" in cmds
        assert "git branch -D feat/T1-g0" in cmds

    def test_refuses_empty_and_unknown_workspace(self):
        lc = _lifecycle()
        with pytest.raises(lc.LifecycleRefused):
            lc.compose_join(tasks=[])
        with pytest.raises(lc.LifecycleRefused):
            lc.compose_join(tasks=[{"task_id": "T1"}])


class TestGateComplete:
    def test_passes_clean_commit_verify_revision(self):
        lc = _lifecycle()
        status = {"clean": True, "branch_exists": True,
                  "commits_since_claim": 2, "head": "abc"}
        assert lc.gate_complete(status=status, verify_ok=True,
                                expected_revision=60,
                                live_revision=60) is None

    def test_refuses_unclean_no_commit_red_verify_stale(self):
        lc = _lifecycle()
        good = {"clean": True, "branch_exists": True,
                "commits_since_claim": 1, "head": "abc"}
        with pytest.raises(lc.LifecycleRefused):
            lc.gate_complete(status=dict(good, clean=False), verify_ok=True,
                             expected_revision=60, live_revision=60)
        with pytest.raises(lc.LifecycleRefused):
            lc.gate_complete(status=dict(good, commits_since_claim=0),
                             verify_ok=True, expected_revision=60,
                             live_revision=60)
        with pytest.raises(lc.LifecycleRefused):
            lc.gate_complete(status=good, verify_ok=False,
                             expected_revision=60, live_revision=60)
        with pytest.raises(lc.LifecycleRefused):
            lc.gate_complete(status=good, verify_ok=True,
                             expected_revision=59, live_revision=60)


def _init_repo(repo: Path) -> str:
    subprocess.run(["git", "init"], cwd=repo, check=True,
                   capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo,
                   check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True,
                   capture_output=True)
    (repo / "f.txt").write_text("hi")
    subprocess.run(["git", "add", "."], cwd=repo, check=True,
                   capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True,
                   capture_output=True)
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True,
                         capture_output=True, text=True)
    return out.stdout.strip()


class TestStatusChecks:
    def test_fails_closed_on_git_errors(self, tmp_path):
        lc = _lifecycle()
        got = lc.status_checks(path=str(tmp_path / "nope"),
                               branch="feat/T1-g0", base_commit="unknown")
        assert got["clean"] is False

    def test_reads_real_repo(self, tmp_path):
        lc = _lifecycle()
        repo = tmp_path / "repo"
        repo.mkdir()
        base = _init_repo(repo)
        cur = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                             cwd=repo, check=True, capture_output=True,
                             text=True).stdout.strip()
        got = lc.status_checks(path=str(repo), branch=cur, base_commit=base)
        assert got["clean"] is True
        assert got["branch_exists"] is True
        assert got["commits_since_claim"] == 0


def _b_state():
    from net import state  # noqa: PLC0415
    return state


def _seed_bundle(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
    monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
    state = _b_state()
    state.init_empty(tmp_path)
    st = state.load(tmp_path)
    for place, tokens in (
        ("work_pending", 1),
        ("work_active", 0),
        ("work_done", 0),
        ("agent_attention", 1),
        ("feature_ready", 1),
        ("worker_slots", 2),
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
        "work_pending": 1,
        "work_active": 0,
        "work_done": 0,
        "agent_attention": 1,
        "feature_ready": 1,
        "worker_slots": 2,
    }
    st.task_bindings = [
        {"id": "t-1", "place": "work_pending", "generation": 0,
         "scope": ["src/a.py"]},
    ]
    state.save(tmp_path, st)
    return tmp_path


def _b_ledger(tmp_path: Path):
    import json as _json
    rows = []
    ledger = tmp_path / "ledger.jsonl"
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").strip().splitlines():
            if line.strip():
                rows.append(_json.loads(line))
    return rows


class TestDispatchSidecar:
    def test_dispatch_stamps_session_sidecar(self, monkeypatch, tmp_path):
        base = _seed_bundle(monkeypatch, tmp_path)
        state = _b_state()
        view = state.plan_dispatch_view(base)
        assert len(view["plan"]) == 1
        assert view["plan"][0]["sidecar"]["branch"] == "feat/t-1-g1"
        st, report = state.dispatch_claims(
            base, plan=view, reasoning="b", session="b",
            expected_revision=0,
        )
        assert st.revision == 1
        b = next(x for x in state.load(base).task_bindings
                 if x["id"] == "t-1")
        assert b["place"] == "work_done"
        assert b["workspace"]["sidecar"]["branch"] == "feat/t-1-g1"
        assert b["workspace"]["sidecar"]["path"] == ".sandbox/bench/t-1-g1"
        assert report["tasks"][0]["sidecar"]["branch"] == "feat/t-1-g1"
        claims = [r for r in _b_ledger(tmp_path)
                  if r.get("kind") == "net_claim"]
        assert len(claims) == 1
        assert claims[0]["sidecar"]["branch"] == "feat/t-1-g1"

    def test_preview_creates_no_sidecar_fs(self, monkeypatch, tmp_path):
        base = _seed_bundle(monkeypatch, tmp_path)
        state = _b_state()
        view = state.plan_dispatch_view(base)
        assert view["plan"][0]["sidecar"]["path"] == ".sandbox/bench/t-1-g1"
        assert not (Path(".sandbox/bench/t-1-g1").exists())
