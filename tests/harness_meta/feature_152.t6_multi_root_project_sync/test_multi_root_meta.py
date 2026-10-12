# tests/harness_meta/feature_152.t6_multi_root_project_sync/test_multi_root_meta.py
# — feature_152 T6 multi-root project sync goldens (design_001 + operation_spec).
#
# Hermetic multi-root: OMT_PROJECTS_ROOT UNSET → discovery anchors at
# projects_archive().parent (tmp/.projects — zero new env vars, feature_152
# design §Roots); OMT_NET_DIR points at an unbootstrapped tmp dir so the
# fail-open lifecycle hook stays silent; OMT_LEDGER_PATH/OMT_WORK_PATH per-call.
# RED-runnable: projects_roots/find_home/move are absent at RED → failures
# surface as test failures, not collection errors (030 GOTCHA precedent).
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = REPO_ROOT / "scripts" / "omt"

sys.path.insert(0, str(SCRIPT_DIR))


def _mod(name: str):
    """Import scripts/omt/<name>.py (lazy — attrs may not exist at RED)."""
    if str(SCRIPT_DIR) in sys.path:
        return importlib.import_module(name)
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _records(ledger: Path) -> list[dict]:
    if not ledger.exists():
        return []
    return [json.loads(x) for x in ledger.read_text().splitlines() if x.strip()]


_WORK_TMPL = ("# WORK\n\n## Tasks\n\n- [ ] **feature_001.x**\n\n---\n\n"
              "## Agent Scratchpad\n\n```\nscratch\n```\n")


@pytest.fixture()
def menv(tmp_path, monkeypatch):
    """Multi-root hermetic: two roots under tmp/.projects, discovery mode
    (OMT_PROJECTS_ROOT unset), archive anchors the parent, net unbootstrapped."""
    parent = tmp_path / ".projects"
    meta, agentx, arch = parent / "meta", parent / "agentx", parent / "archive"
    for d in (meta, agentx, arch):
        d.mkdir(parents=True)
    ledger = tmp_path / "ledger.jsonl"
    work = tmp_path / "WORK.md"
    work.write_text(_WORK_TMPL)
    monkeypatch.setenv("OMT_LEDGER_PATH", str(ledger))
    monkeypatch.setenv("OMT_PROJECTS_ARCHIVE", str(arch))
    monkeypatch.setenv("OMT_WORK_PATH", str(work))
    monkeypatch.setenv("OMT_NET_DIR", str(tmp_path / "net_absent"))
    monkeypatch.delenv("OMT_PROJECTS_ROOT", raising=False)  # multi-root discovery
    return {"ledger": ledger, "work": work, "tmp": tmp_path,
            "parent": parent, "meta": meta, "agentx": agentx, "archive": arch}


@pytest.fixture()
def senv(tmp_path, monkeypatch):
    """Single-root compat: OMT_PROJECTS_ROOT set (030 idiom) — union/manifests
    must scope to the env root even with sibling roots present."""
    parent = tmp_path / ".projects"
    meta, agentx, arch = parent / "meta", parent / "agentx", parent / "archive"
    for d in (meta, agentx, arch):
        d.mkdir(parents=True)
    ledger = tmp_path / "ledger.jsonl"
    work = tmp_path / "WORK.md"
    work.write_text(_WORK_TMPL)
    monkeypatch.setenv("OMT_LEDGER_PATH", str(ledger))
    monkeypatch.setenv("OMT_PROJECTS_ROOT", str(meta))
    monkeypatch.setenv("OMT_PROJECTS_ARCHIVE", str(arch))
    monkeypatch.setenv("OMT_WORK_PATH", str(work))
    monkeypatch.setenv("OMT_NET_DIR", str(tmp_path / "net_absent"))
    (agentx / "other_prod").mkdir()  # sibling-root home: must stay invisible
    return {"ledger": ledger, "work": work, "tmp": tmp_path,
            "parent": parent, "meta": meta, "agentx": agentx, "archive": arch}


def _row_for(text: str, slug: str) -> str:
    rows = [ln for ln in text.splitlines() if ln.startswith(f"| {slug} ")]
    assert rows, f"no ## Projects row for {slug}"
    return rows[0]


class TestMultiRootSync:
    """Union + per-root manifests + single-root compat scoping."""

    def test_union_writes_both_roots_and_idempotent(self, menv):
        project, ps = _mod("project"), _mod("project_state")
        assert project.main(["new", "meta one"]) == 0
        assert project.main(["new", "prod thing", "--root", "agentx"]) == 0
        assert project.main(["link", "feature_150.x", "meta_one"]) == 0
        assert project.main(["link", "feature_151.x", "prod_thing"]) == 0
        assert project.main(["sync"]) == 0
        text = menv["work"].read_text()
        assert "meta_one" in text and "prod_thing" in text  # UNION: both roots
        assert text.index("| prod_thing") < text.index("| meta_one")  # root order agentx<meta
        assert "## Tasks" in text and "scratch" in text  # other sections untouched
        assert re.search(r"\| prod_thing \| active \| feature_151\.x \|", text)
        # byte-stable second sync + round-trip against the builder
        first = text
        assert project.main(["sync"]) == 0
        assert menv["work"].read_text() == first
        recs = ps.read_ledger_all()
        links = ps.derive_links(recs)
        assert ps.extract_work_projects_section(first) == ps.build_work_projects_section(recs, links)
        assert ps.upsert_work_projects(recs, links) is False  # already fresh

    def test_per_root_manifests_list_own_homes(self, menv):
        project = _mod("project")
        project.main(["new", "meta one"])
        project.main(["new", "prod thing", "--root", "agentx"])
        assert project.main(["sync"]) == 0
        meta_manifest = (menv["meta"] / "META.md").read_text()
        agentx_manifest = (menv["agentx"] / "META.md").read_text()
        assert "meta_one" in meta_manifest and "prod_thing" not in meta_manifest
        assert "prod_thing" in agentx_manifest and "meta_one" not in agentx_manifest
        assert "`.projects/meta/<slug>/" in meta_manifest       # convention names its root
        assert "`.projects/agentx/<slug>/" in agentx_manifest

    def test_env_compat_single_root_scopes_to_env_root(self, senv):
        project = _mod("project")
        assert project.main(["new", "in meta"]) == 0
        assert project.main(["sync"]) == 0
        text = senv["work"].read_text()
        assert "in_meta" in text and "other_prod" not in text   # union scoped to env root
        assert (senv["meta"] / "META.md").exists()
        assert not (senv["agentx"] / "META.md").exists()        # no sibling manifests


class TestMoveOp:
    """move: relocation + record + state transparency + WORK.md invisibility."""

    def test_move_relocates_and_records_state_transparent(self, menv):
        project, ps = _mod("project"), _mod("project_state")
        project.main(["new", "moving prod"])
        project.main(["link", "feature_140.x", "moving_prod"])
        assert (menv["meta"] / "moving_prod").is_dir()
        assert project.main(["move", "moving_prod", "--to-root", "agentx"]) == 0
        assert (menv["agentx"] / "moving_prod").is_dir()
        assert not (menv["meta"] / "moving_prod").exists()
        moves = [r for r in _records(menv["ledger"])
                 if r.get("kind") == "project" and r.get("op") == "move"]
        assert len(moves) == 1 and moves[0]["project"] == "moving_prod"
        assert moves[0]["from_root"] == "meta" and moves[0]["to_root"] == "agentx"
        recs = ps.read_ledger_all()
        links = ps.derive_links(recs)
        assert ps.derive_state("moving_prod", recs, links) == "active"  # transparency
        events = ps.project_events(recs, "moving_prod")
        assert events[-1]["op"] == "move"                              # last event reflects it
        assert "moving_prod" in (menv["agentx"] / "META.md").read_text()
        assert "moving_prod" not in (menv["meta"] / "META.md").read_text()

    def test_move_keeps_work_row_byte_identical(self, menv):
        project = _mod("project")
        project.main(["new", "frozen row"])
        project.main(["link", "feature_141.x", "frozen_row"])
        project.main(["sync"])
        before = _row_for(menv["work"].read_text(), "frozen_row")
        assert project.main(["move", "frozen_row", "--to-root", "agentx"]) == 0
        after = _row_for(menv["work"].read_text(), "frozen_row")
        assert before == after  # moves are WORK.md-invisible (slug|state|features)

    def test_move_noop_writes_no_record(self, menv, capsys):
        project = _mod("project")
        project.main(["new", "stays put"])
        rc = project.main(["move", "stays_put", "--to-root", "meta"])
        assert rc == 0
        assert "already at root" in capsys.readouterr().out
        moves = [r for r in _records(menv["ledger"])
                 if r.get("kind") == "project" and r.get("op") == "move"]
        assert moves == []

    def test_move_guards(self, menv, capsys):
        project = _mod("project")
        # unknown slug
        assert project.main(["move", "ghost", "--to-root", "agentx"]) == 2
        assert "unknown project home 'ghost'" in capsys.readouterr().err
        # unknown root
        project.main(["new", "rooted"])
        assert project.main(["move", "rooted", "--to-root", "nope"]) == 2
        assert "unknown root" in capsys.readouterr().err
        # destination occupied by a non-dir straggler (find_home counts dirs
        # only, so the file at the dest is invisible to the collision check)
        project.main(["new", "colliding"])
        (menv["agentx"] / "colliding").write_text("straggler")
        assert project.main(["move", "colliding", "--to-root", "agentx"]) == 2
        assert "already exists" in capsys.readouterr().err
        (menv["agentx"] / "colliding").unlink()
        # slug in multiple roots → collision invariant
        (menv["agentx"] / "colliding").mkdir()
        assert project.main(["move", "colliding", "--to-root", "meta"]) == 2
        assert "multiple roots" in capsys.readouterr().err
        # archived home refuses to move
        project.main(["new", "done thing"])
        project.main(["close", "done_thing"])
        project.main(["archive", "done_thing"])
        assert project.main(["move", "done_thing", "--to-root", "agentx"]) == 2
        assert "archived" in capsys.readouterr().err


class TestNewRootFlag:
    """new --root: birth in the named root + cross-root collision guard."""

    def test_new_root_flag_and_collision(self, menv, capsys):
        project = _mod("project")
        assert project.main(["new", "born prod", "--root", "agentx"]) == 0
        assert (menv["agentx"] / "born_prod" / "PROJECT.md").exists()
        assert "created project home .projects/agentx/born_prod" in capsys.readouterr().out
        assert project.main(["new", "default home"]) == 0               # default meta
        assert (menv["meta"] / "default_home").is_dir()
        assert project.main(["new", "born prod", "--root", "meta"]) == 2  # collision
        assert "already exists" in capsys.readouterr().err


class TestCrossRootLookups:
    """link/log/backfill resolve homes in non-default roots without env overrides."""

    def test_link_log_backfill_cross_root(self, menv, capsys):
        project = _mod("project")
        assert project.main(["new", "solo prod", "--root", "agentx"]) == 0
        assert project.main(["link", "feature_152.y", "solo_prod"]) == 0  # no env override
        assert project.main(["log", "solo_prod", "cross-root note"]) == 0
        state_text = (menv["agentx"] / "solo_prod" / "CURRENT_STATE.md").read_text()
        assert "cross-root note" in state_text
        # backfill adopts a pre-mechanic home in a non-default root
        adopted = menv["agentx"] / "adopted_home"
        adopted.mkdir()
        (adopted / "PROJECT.md").write_text("# PROJECT: adopted_home\n\n> Status: **draft**\n")
        assert project.main(["backfill", "adopted_home"]) == 0
        creates = [r for r in _records(menv["ledger"])
                   if r.get("kind") == "project" and r.get("op") == "create"
                   and r.get("project") == "adopted_home"]
        assert len(creates) == 1
        # slug collision is fatal to lookups
        (menv["meta"] / "solo_prod").mkdir()
        assert project.main(["link", "feature_152.z", "solo_prod"]) == 2
        assert "multiple roots" in capsys.readouterr().err


class TestDeriveStateMoveTransparency:
    """move never becomes a lifecycle last-op (FSM unchanged)."""

    def test_derive_state_ignores_move_ops(self):
        ps = _mod("project_state")
        records = [{"kind": "project", "op": "create", "project": "p"}]
        links: dict[str, dict] = {}
        assert ps.derive_state("p", records, links) == "draft"
        links["feature_001.a"] = {"project": "p", "origin": "manual", "ts": "t"}
        assert ps.derive_state("p", records, links) == "active"
        records.append({"kind": "project", "op": "move", "project": "p",
                        "from_root": "meta", "to_root": "agentx"})
        assert ps.derive_state("p", records, links) == "active"   # move is transparent
        records.append({"kind": "project", "op": "close", "project": "p"})
        assert ps.derive_state("p", records, links) == "complete"
        records.append({"kind": "project", "op": "move", "project": "p",
                        "from_root": "agentx", "to_root": "meta"})
        assert ps.derive_state("p", records, links) == "complete"  # still transparent
