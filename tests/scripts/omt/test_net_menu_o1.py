"""O1 whole-project menu composer goldens — feature_110.whole_project_menu_composer.

Pure render (sync_md.compose_menu_options / lanes_line / render_tasks_block /
menu_lines) + threaded state.sync net_to_md dry-run menu inputs.

Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_NET_FEATURES_DIR /
OMT_NET_WORK_MD. Hygiene git-fallback is live-read fail-open: goldens assert
shape/sort, never exact live counts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))


def _sync_md():
    from net import sync_md  # noqa: PLC0415

    return sync_md


def _state():
    from net import state  # noqa: PLC0415

    return state


WORK_MD_O1 = """# WORK

## Tasks

<!-- net_rev:60 -->
NEXT: none
Other enabled: none
Blocked: none
Resources: none
Pool: pending=0 active=0 done=7 (places 15/15)

## Projects (synced by `uv run scripts/omt/project.py sync` — do not hand-edit)

| project | state | features |
|---|---|---|
| petri_net_studio | active | feature_032.petri_net_format |
| rag_v2 | active | feature_027.rag_v2 |
| workflows | draft | — |

---
PENDING FEATURES (next work):
- feature_001.session_user_objectives_driven_by_Petri_Net — scope & success criteria unset.
- feature_002.rag_retrieval_augmented_generation — scope & success criteria unset.
"""


def _env(tmp_path, monkeypatch, work_text: str = WORK_MD_O1):
    net_dir = tmp_path / "net"
    monkeypatch.setenv("OMT_NET_DIR", str(net_dir))
    monkeypatch.setenv("OMT_LEDGER_PATH", str(net_dir / "ledger.jsonl"))
    features = tmp_path / "features"
    features.mkdir(exist_ok=True)
    (features / "feature_001.alpha").mkdir(exist_ok=True)
    work = tmp_path / "WORK.md"
    work.write_text(work_text, encoding="utf-8")
    monkeypatch.setenv("OMT_NET_FEATURES_DIR", str(features))
    monkeypatch.setenv("OMT_NET_WORK_MD", str(work))
    return tmp_path


class TestComposeMenuOptions:
    def test_projects_dict_sorted_proj_ids(self) -> None:
        sync_md = _sync_md()
        opts = sync_md.compose_menu_options(
            {"rag_v2": "active", "petri_net_studio": "active"}
        )
        assert opts == [
            ("proj:petri_net_studio", "petri_net_studio (active)"),
            ("proj:rag_v2", "rag_v2 (active)"),
        ]

    def test_projects_hygiene_unscoped_stable_order(self) -> None:
        sync_md = _sync_md()
        opts = sync_md.compose_menu_options(
            projects=[{"slug": "rag_v2", "state": "active", "features": "f"}],
            hygiene=[{"class": "aging-draft", "key": "workflows", "detail": "d"}],
            unscoped=[{"id": "001", "note": "scope unset"}],
        )
        ids = [oid for oid, _ in opts]
        assert ids == [
            "proj:rag_v2",
            "drift:aging-draft:workflows",
            "unscoped:001",
        ]


class TestLanesLine:
    def test_verification_integration_deadlock_blocked(self) -> None:
        sync_md = _sync_md()
        text = sync_md.lanes_line(
            {
                "verification": {"used": 0, "total": 1, "free": 1},
                "integration": {"used": 0, "total": 1, "free": 1},
                "deadlocks_complete": True,
            },
            [{"transition": "f001_start"}],
        )
        assert text is not None
        assert "verification 0/1 free 1" in text
        assert "integration 0/1 free 1" in text
        assert "deadlocks_complete" in text
        assert "blocked:f001_start" in text

    def test_none_when_no_lanes(self) -> None:
        sync_md = _sync_md()
        assert sync_md.lanes_line(None, []) is None


class TestRenderTasksBlockO1:
    def _net(self, tmp_path, monkeypatch):
        _env(tmp_path, monkeypatch)
        state = _state()
        sync_md = _sync_md()
        st_mod = state
        base = tmp_path / "net"
        st, _ = st_mod.sync(base, reasoning="bootstrap", session="s1")
        _, info = st_mod.sync(base, reasoning="resync", session="s1")
        for entry in info["proposal"]["add_subnets"]:
            st_mod.splice(
                base, "add", mutation=entry["mutation"],
                reasoning="test apply", session="s1", feature="feature_110",
            )
        return st_mod.load(base)

    def test_empty_enabled_uses_first_option_as_next(self, tmp_path, monkeypatch) -> None:
        st_mod = _state()
        base = tmp_path / "net"
        st = self._net(tmp_path, monkeypatch)
        # Drain the single f001_start so enabled[] is empty → NEXT falls back to options (G2).
        st_mod.fire(base, "f001_start", reasoning="drain for empty-menu", session="s1")
        st = st_mod.load(base)
        sync_md = _sync_md()
        text = sync_md.render_tasks_block(
            st.net, st.live_marking, st.overlay,
            resources=[], conflicts=[], revision=st.revision, slugs={},
            projects=[{"slug": "rag_v2", "state": "active", "features": "f"}],
            hygiene=[], unscoped=[{"id": "001", "note": "scope unset"}],
            lanes=None,
        )
        assert "NEXT: proj:rag_v2 (recommended)" in text
        assert "Options: proj:rag_v2, unscoped:001" in text
        # Trimmed for work_md budget: persisted block keeps Options IDs line only
        # (per-option labels live in compose_menu_options, not in WORK.md).
        assert "- [ ] **proj:rag_v2**" not in text
        # D19 ordering (non-pool net: no Pool line): NEXT < Other < Blocked < Resources < Options
        for marker in ("NEXT:", "Other enabled:", "Blocked:", "Resources:", "Options:"):
            assert marker in text, marker
        idx = [text.index(m) for m in ("NEXT:", "Other enabled:", "Blocked:", "Resources:", "Options:")]
        assert idx == sorted(idx)

    def test_enabled_wins_over_options(self, tmp_path, monkeypatch) -> None:
        st = self._net(tmp_path, monkeypatch)
        sync_md = _sync_md()
        text = sync_md.render_tasks_block(
            st.net, st.live_marking, st.overlay,
            resources=[], conflicts=[], revision=st.revision, slugs={},
            projects=[{"slug": "rag_v2", "state": "active", "features": "f"}],
            hygiene=[], unscoped=[], lanes=None,
        )
        # enabled[] non-empty in this bootstrap → NEXT is pool transition, options still listed
        assert "Options: proj:rag_v2" in text
        assert "NEXT: " in text and "(recommended)" in text

    def test_lanes_line_appended(self, tmp_path, monkeypatch) -> None:
        st = self._net(tmp_path, monkeypatch)
        sync_md = _sync_md()
        text = sync_md.render_tasks_block(
            st.net, st.live_marking, st.overlay,
            resources=[], conflicts=[], revision=st.revision, slugs={},
            projects=[], hygiene=[], unscoped=[],
            lanes={"verification": {"used": 0, "total": 1, "free": 1},
                   "integration": {"used": 0, "total": 1, "free": 1}},
        )
        assert "Lanes: verification 0/1 free 1, integration 0/1 free 1" in text


class TestMenuLinesO1:
    def test_menu_lines_empty_enabled_uses_option(self) -> None:
        sync_md = _sync_md()
        lines = sync_md.menu_lines(
            enabled=[], resources=[], conflicts=[], revision=60,
            projects=[{"slug": "rag_v2", "state": "active", "features": "f"}],
            hygiene=[{"class": "aging-draft", "key": "workflows", "detail": "d"}],
            unscoped=[{"id": "001", "note": "scope unset"}],
            lanes={"verification": {"used": 0, "total": 1, "free": 1},
                   "integration": {"used": 0, "total": 1, "free": 1}},
        )
        blob = "\n".join(lines)
        assert "NEXT: proj:rag_v2 (recommended)" in blob
        assert "Options: proj:rag_v2, drift:aging-draft:workflows, unscoped:001" in blob
        assert "Lanes: verification 0/1 free 1" in blob
        assert "(net rev 60)" in blob


class TestStateHelpersO1:
    def test_projects_from_work_slug_sorted(self, tmp_path, monkeypatch) -> None:
        _env(tmp_path, monkeypatch)
        state = _state()
        rows = state._menu_projects_from_work()
        assert [r["slug"] for r in rows] == ["petri_net_studio", "rag_v2", "workflows"]
        assert all(r["state"] in ("active", "draft") for r in rows)

    def test_unscoped_scoped_to_pending_block_only(self, tmp_path, monkeypatch) -> None:
        _env(tmp_path, monkeypatch)
        state = _state()
        ids = sorted(u["id"] for u in state._menu_unscoped())
        assert ids == ["001", "002"]

    def test_lanes_none_without_lane_places(self, tmp_path, monkeypatch) -> None:
        _env(tmp_path, monkeypatch)
        state = _state()
        assert state._menu_lanes({"work_pending": 0}) is None

    def test_lanes_dict_with_lane_places(self, tmp_path, monkeypatch) -> None:
        _env(tmp_path, monkeypatch)
        state = _state()
        lanes = state._menu_lanes(
            {"work_verifying": 1, "work_integration_ready": 0, "work_integrating": 0}
        )
        assert lanes is not None
        assert lanes["verification"]["used"] == 1
        assert lanes["integration"]["free"] == 1

    def test_hygiene_fail_open_sorted(self, tmp_path, monkeypatch) -> None:
        _env(tmp_path, monkeypatch)
        state = _state()
        hygiene = state._menu_hygiene([{"slug": "workflows", "state": "draft", "features": "—"}])
        assert isinstance(hygiene, list)
        keys = [(h.get("class", ""), h.get("key", "")) for h in hygiene]
        assert keys == sorted(keys)

    def test_sync_dry_run_threads_menu(self, tmp_path, monkeypatch) -> None:
        base_holder = _env(tmp_path, monkeypatch)
        state = _state()
        base = base_holder / "net"
        st, _ = state.sync(base, reasoning="bootstrap", session="s1")
        _, info = state.sync(base, reasoning="resync", session="s1")
        for entry in info["proposal"]["add_subnets"]:
            state.splice(
                base, "add", mutation=entry["mutation"],
                reasoning="test apply", session="s1", feature="feature_110",
            )
        _, info2 = state.sync(
            base, reasoning="menu threading", session="s1",
            direction="net_to_md", dry_run=True,
        )
        assert "rendered" in info2 and "menu" in info2, info2.keys()
        menu = info2.get("menu", {})
        assert menu.get("projects") == 3, menu
        assert menu.get("unscoped") == 2, menu
        assert "proj:rag_v2" in info2.get("rendered", "")
        assert "unscoped:001" in info2.get("rendered", "")
        # dry-run must not write WORK.md Tasks region
        work_text = (base_holder / "WORK.md").read_text(encoding="utf-8")
        assert "<!-- net_rev:60 -->" in work_text
