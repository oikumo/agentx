"""MVC++ compliance tests for feature_013.ai_model_provider_selector.

Verifies the architecture rules (guide §5, §16) for every file the feature
touches/creates:
  - View does not import Model (``agentx.model.*``).
  - Model does not import ui (``agentx.ui.*``).
  - Abstract Partner is an ``ABC`` with ``@abstractmethod``.
  - No SQL outside DP classes (N/A here — JSON persistence; assert no sqlite).
  - No ``*Controller`` name under ``model/``.
  - ``scripts/omt/mvc_check.py`` reports 0 errors for the touched files.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src" / "agentx"

# Files created/touched by feature_013.
NEW_FILES = [
    SRC / "model" / "ai" / "model_registry.py",
    SRC / "ui" / "screens" / "models" / "models_controller.py",
    SRC / "ui" / "tui" / "screens" / "models_screen.py",
]
TOUCHED_FILES = [
    SRC / "model" / "ai" / "providers.py",
    SRC / "model" / "ai" / "service.py",
    SRC / "agent" / "model" / "ai_adapter.py",
    SRC / "ui" / "screens" / "main" / "main_controller.py",
    SRC / "ui" / "tui" / "screens" / "main_screen.py",
    SRC / "ui" / "tui" / "framework" / "widgets.py",
    SRC / "ui" / "screens" / "chat" / "chat_controller.py",
    SRC / "ui" / "screens" / "rag" / "rag_chat_controller.py",
    SRC / "model" / "rag" / "rag.py",
]
ALL_FILES = NEW_FILES + TOUCHED_FILES


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# ===========================================================================
# Layer isolation
# ===========================================================================


VIEW_FILES = [
    SRC / "ui" / "tui" / "screens" / "models_screen.py",
    SRC / "ui" / "tui" / "screens" / "main_screen.py",
    SRC / "ui" / "tui" / "framework" / "widgets.py",
]
MODEL_FILES = [
    SRC / "model" / "ai" / "model_registry.py",
    SRC / "model" / "ai" / "providers.py",
    SRC / "model" / "ai" / "service.py",
    SRC / "model" / "rag" / "rag.py",
]


class TestLayerIsolation:
    @pytest.mark.parametrize("f", VIEW_FILES, ids=lambda f: str(f.relative_to(SRC)))
    def test_view_does_not_import_model(self, f: Path) -> None:
        text = _read(f)
        assert "from agentx.model" not in text, (
            f"{f}: View imports Model — MVC++ violation (guide §5)"
        )
        assert "import agentx.model" not in text, (
            f"{f}: View imports Model — MVC++ violation (guide §5)"
        )

    @pytest.mark.parametrize("f", MODEL_FILES, ids=lambda f: str(f.relative_to(SRC)))
    def test_model_does_not_import_ui(self, f: Path) -> None:
        text = _read(f)
        assert "from agentx.ui" not in text, (
            f"{f}: Model imports ui — MVC++ violation (guide §5)"
        )
        assert "import agentx.ui" not in text, (
            f"{f}: Model imports ui — MVC++ violation (guide §5)"
        )


# ===========================================================================
# Abstract Partner
# ===========================================================================


class TestAbstractPartner:
    def test_imodelsviewpartner_is_abc(self) -> None:
        from abc import ABC

        from agentx.ui.screens.models.models_controller import IModelsViewPartner

        assert issubclass(IModelsViewPartner, ABC)

    def test_imodelsviewpartner_has_abstractmethods(self) -> None:
        from agentx.ui.screens.models.models_controller import IModelsViewPartner

        assert len(IModelsViewPartner.__abstractmethods__) >= 4
        for name in ("list_providers", "get_current_id", "select_provider", "get_status_text"):
            assert name in IModelsViewPartner.__abstractmethods__

    def test_modelscontroller_implements_partner(self) -> None:
        from agentx.ui.screens.models.models_controller import (
            IModelsViewPartner,
            ModelsController,
        )

        assert issubclass(ModelsController, IModelsViewPartner)
        # no remaining abstractmethods once instantiated
        assert not ModelsController.__abstractmethods__


# ===========================================================================
# No SQL outside DP / no Controller under model/
# ===========================================================================


class TestNoSqlOrControllerInModel:
    @pytest.mark.parametrize(
        "f",
        [SRC / "model" / "ai" / "model_registry.py"],
        ids=["model_registry.py"],
    )
    def test_no_sql_in_registry(self, f: Path) -> None:
        text = _read(f)
        for needle in ("sqlite3", ".execute(", "SELECT ", "INSERT ", "UPDATE ", "DELETE "):
            assert needle not in text, f"{f}: found SQL '{needle}' outside a DP class"

    def test_no_controller_named_file_under_model(self) -> None:
        controllers = list((SRC / "model").rglob("*controller*.py"))
        assert controllers == [], (
            f"Found *controller*.py under model/ (guide §16 #9): {controllers}"
        )


# ===========================================================================
# mvc_check.py — 0 errors for touched files
# ===========================================================================


class TestMvcCheckTool:
    def test_mvc_check_zero_errors_for_feature_files(self) -> None:
        """Run the project's MVC++ linter on all feature_013 files."""
        result = subprocess.run(
            ["uv", "run", "scripts/omt/mvc_check.py", *map(str, ALL_FILES)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        out = result.stdout
        # The tool prints "N error(s)"; ensure 0 errors.
        assert " 0 error" in out, f"mvc_check reported errors:\n{out}"
