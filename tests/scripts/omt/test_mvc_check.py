#!/usr/bin/env python3
"""Unit tests for mvc_check.py — OMT++ MVC++ architecture linter.

Tests cover all ERROR and WARNING rules from guide §16 "Common Mistakes to Catch".
Run with: uv run pytest tests/scripts/omt/test_mvc_check.py -v
"""
from __future__ import annotations

import tempfile
import sys
from pathlib import Path

# Add scripts/omt to path for importing mvc_check
SCRIPTS_DIR = Path(__file__).parent.parent.parent.parent / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))

import mvc_check


class TestViewImportsModel:
    """Tests for VIEW_IMPORTS_MODEL error rule."""

    def test_view_imports_model_error(self):
        code = '''
from model.session import Session

class MainView:
    pass
'''
        with tempfile.NamedTemporaryFile(suffix="_view.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert any(f.rule == "VIEW_IMPORTS_MODEL" and f.severity == "error" for f in findings)

    def test_view_imports_model_from_submodule(self):
        code = '''
from model.rag.rag import Rag

class MainView:
    pass
'''
        with tempfile.NamedTemporaryFile(suffix="_view.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert any(f.rule == "VIEW_IMPORTS_MODEL" and f.severity == "error" for f in findings)

    def test_non_view_file_not_checked(self):
        code = '''
from model.session import Session

class MainController:
    pass
'''
        with tempfile.NamedTemporaryFile(suffix="_controller.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert not any(f.rule == "VIEW_IMPORTS_MODEL" for f in findings)


class TestModelImportsUI:
    """Tests for MODEL_IMPORTS_UI error rule."""

    def test_model_imports_ui_error(self):
        code = '''
from ui.screens.main.main_view import MainView

class Session:
    pass
'''
        with tempfile.NamedTemporaryFile(suffix=".py", dir=tempfile.mkdtemp(), mode="w", delete=False) as f:
            # Create a model/ directory structure
            import os
            model_dir = Path(f.name).parent / "model"
            model_dir.mkdir(exist_ok=True)
            model_file = model_dir / "session.py"
            model_file.write_text(code)
            findings = mvc_check.check_file(model_file)

        assert any(f.rule == "MODEL_IMPORTS_UI" and f.severity == "error" for f in findings)


class TestControllerInModel:
    """Tests for CONTROLLER_IN_MODEL error rule."""

    def test_controller_class_in_model_dir_error(self):
        import os
        temp_dir = tempfile.mkdtemp()
        model_dir = Path(temp_dir) / "model" / "session"
        model_dir.mkdir(parents=True, exist_ok=True)
        model_file = model_dir / "session_controller.py"
        
        code = '''
class SessionController:
    pass
'''
        model_file.write_text(code)
        findings = mvc_check.check_file(model_file)

        assert any(f.rule == "CONTROLLER_IN_MODEL" and f.severity == "error" for f in findings)

    def test_manager_class_in_model_ok(self):
        import os
        temp_dir = tempfile.mkdtemp()
        model_dir = Path(temp_dir) / "model" / "session"
        model_dir.mkdir(parents=True, exist_ok=True)
        model_file = model_dir / "session_manager.py"
        
        code = '''
class SessionManager:
    pass
'''
        model_file.write_text(code)
        findings = mvc_check.check_file(model_file)

        assert not any(f.rule == "CONTROLLER_IN_MODEL" for f in findings)


class TestPartnerNotABC:
    """Tests for PARTNER_NOT_ABC error rule."""

    def test_partner_without_abc_error(self):
        code = '''
class IMainViewPartner:
    def on_user_input(self, user_input: str) -> None:
        pass
'''
        with tempfile.NamedTemporaryFile(suffix="_view.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert any(f.rule == "PARTNER_NOT_ABC" and f.severity == "error" for f in findings)

    def test_partner_with_abc_ok(self):
        code = '''
from abc import ABC, abstractmethod

class IMainViewPartner(ABC):
    @abstractmethod
    def on_user_input(self, user_input: str) -> None:
        pass
'''
        with tempfile.NamedTemporaryFile(suffix="_view.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert not any(f.rule == "PARTNER_NOT_ABC" for f in findings)

    def test_non_partner_class_ok(self):
        code = '''
class SomeHelper:
    def do_something(self) -> None:
        pass
'''
        with tempfile.NamedTemporaryFile(suffix="_view.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert not any(f.rule == "PARTNER_NOT_ABC" for f in findings)


class TestViewCreatesController:
    """Tests for VIEW_CREATES_CONTROLLER error rule."""

    def test_view_creates_controller_error(self):
        code = '''
class MainView:
    def __init__(self):
        self.controller = MainController()
'''
        with tempfile.NamedTemporaryFile(suffix="_view.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert any(f.rule == "VIEW_CREATES_CONTROLLER" and f.severity == "error" for f in findings)

    def test_view_receives_partner_ok(self):
        code = '''
class MainView:
    def __init__(self, partner: IMainViewPartner):
        self._partner = partner
'''
        with tempfile.NamedTemporaryFile(suffix="_view.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert not any(f.rule == "VIEW_CREATES_CONTROLLER" for f in findings)


class TestControllerUICode:
    """Tests for CONTROLLER_UI_CODE warning rule."""

    def test_controller_with_print_warning(self):
        code = '''
class MainController:
    def show_message(self):
        print("Hello")
'''
        with tempfile.NamedTemporaryFile(suffix="_controller.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert any(f.rule == "CONTROLLER_UI_CODE" and f.severity == "warning" for f in findings)

    def test_controller_with_console_warning(self):
        code = '''
class MainController:
    def show_message(self):
        console.print("Hello")
'''
        with tempfile.NamedTemporaryFile(suffix="_controller.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert any(f.rule == "CONTROLLER_UI_CODE" and f.severity == "warning" for f in findings)

    def test_controller_with_rich_import_warning(self):
        code = '''
from rich.console import Console

class MainController:
    pass
'''
        with tempfile.NamedTemporaryFile(suffix="_controller.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert any(f.rule == "CONTROLLER_UI_CODE" and f.severity == "warning" for f in findings)

    def test_non_controller_not_checked(self):
        code = '''
class MainView:
    def show_message(self):
        print("Hello")
'''
        with tempfile.NamedTemporaryFile(suffix="_view.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert not any(f.rule == "CONTROLLER_UI_CODE" for f in findings)


class TestSQLOutsideDP:
    """Tests for SQL_OUTSIDE_DP warning rule."""

    def test_sql_in_controller_warning(self):
        code = '''
class MainController:
    def save(self):
        conn.execute("INSERT INTO foo VALUES (1)")
'''
        with tempfile.NamedTemporaryFile(suffix="_controller.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert any(f.rule == "SQL_OUTSIDE_DP" and f.severity == "warning" for f in findings)

    def test_select_in_non_db_warning(self):
        code = '''
class SomeService:
    def query(self):
        cursor.execute("SELECT * FROM users")
'''
        with tempfile.NamedTemporaryFile(suffix="_service.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert any(f.rule == "SQL_OUTSIDE_DP" and f.severity == "warning" for f in findings)

    def test_sql_in_db_file_ok(self):
        code = '''
class DP_Session:
    def insert(self, session):
        conn.execute("INSERT INTO sessions (name) VALUES (?)", (session.name,))
'''
        with tempfile.NamedTemporaryFile(suffix="_db.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert not any(f.rule == "SQL_OUTSIDE_DP" for f in findings)

    def test_sql_in_comment_ignored(self):
        code = '''
class MainController:
    # This is a comment with SELECT * FROM users
    def do_something(self):
        pass
'''
        with tempfile.NamedTemporaryFile(suffix="_controller.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        # Comments should be ignored (line.split("#", 1)[0])
        assert not any(f.rule == "SQL_OUTSIDE_DP" for f in findings)


class TestGodController:
    """Tests for GOD_CONTROLLER warning rule."""

    def test_god_controller_warning(self):
        # Create a controller with >300 lines
        lines = ["class MainController:"] + [f"    def method_{i}(self): pass" for i in range(310)]
        code = "\n".join(lines)
        
        with tempfile.NamedTemporaryFile(suffix="_controller.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert any(f.rule == "GOD_CONTROLLER" and f.severity == "warning" for f in findings)

    def test_normal_controller_ok(self):
        code = '''
class MainController:
    def method_1(self): pass
    def method_2(self): pass
'''
        with tempfile.NamedTemporaryFile(suffix="_controller.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert not any(f.rule == "GOD_CONTROLLER" for f in findings)


class TestParseError:
    """Tests for PARSE_ERROR handling."""

    def test_syntax_error_reported(self):
        code = '''
class MainController:
    def method(  # Missing closing parenthesis
        pass
'''
        with tempfile.NamedTemporaryFile(suffix="_controller.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        assert any(f.rule == "PARSE_ERROR" and f.severity == "error" for f in findings)


class TestUnicodeHandling:
    """Tests for unicode content handling."""

    def test_unicode_in_strings_no_crash(self):
        code = '''
class MainController:
    def show_message(self):
        print("Héllo Wörld 🎉")  # Unicode in string
        print("中文测试")  # Chinese characters
'''
        with tempfile.NamedTemporaryFile(suffix="_controller.py", mode="w", delete=False, encoding="utf-8") as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        # Should not crash, just report the print warning
        assert any(f.rule == "CONTROLLER_UI_CODE" for f in findings)


class TestCleanFile:
    """Tests for valid MVC++ files."""

    def test_valid_mvc_file_no_violations(self):
        code = '''
from abc import ABC, abstractmethod

class IMainViewPartner(ABC):
    @abstractmethod
    def on_user_input(self, user_input: str) -> None:
        pass

    @abstractmethod
    def get_prompt(self) -> str:
        pass


class MainController(IMainViewPartner):
    def __init__(self):
        self._view = MainView(self)

    def on_user_input(self, user_input: str) -> None:
        pass

    def get_prompt(self) -> str:
        return "(main)"
'''
        with tempfile.NamedTemporaryFile(suffix="_controller.py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            findings = mvc_check.check_file(Path(f.name))

        # Should have no ERRORs (warnings for CONTROLLER_UI_CODE may exist but shouldn't for this code)
        errors = [f for f in findings if f.severity == "error"]
        assert len(errors) == 0


class TestJSONOutput:
    """Tests for --json output format."""

    def test_json_output_structure(self):
        import subprocess
        import json
        
        result = subprocess.run(
            ["uv", "run", "scripts/omt/mvc_check.py", "--json"],
            cwd=Path(__file__).parent.parent.parent.parent,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode in (0, 1)  # 0 = no errors, 1 = errors found
        data = json.loads(result.stdout)
        
        assert "files_scanned" in data
        assert "errors" in data
        assert "warnings" in data
        assert "findings" in data
        assert isinstance(data["findings"], list)


if __name__ == "__main__":
    # Allow running directly with pytest
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))