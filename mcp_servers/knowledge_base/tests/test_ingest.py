"""Tests for `kb.ingest.PythonCodeAnalyzer` and `WorkspaceIngestor`."""

from pathlib import Path

import pytest

from kb.ingest import PythonCodeAnalyzer


def test_analyzer_finds_class_and_its_methods(tmp_path: Path):
    f = tmp_path / "m.py"
    f.write_text(
        "class C:\n"
        "    def a(self):\n"
        "        pass\n"
        "    def b(self):\n"
        "        pass\n"
    )
    elements = PythonCodeAnalyzer(f).analyze()
    types = {(e.type, e.name) for e in elements}
    assert ("class", "C") in types
    assert ("method", "C.a") in types
    assert ("method", "C.b") in types


def test_analyzer_finds_top_level_function(tmp_path: Path):
    f = tmp_path / "m.py"
    f.write_text("def foo():\n    return 1\n")
    elements = PythonCodeAnalyzer(f).analyze()
    assert any(e.type == "function" and e.name == "foo" for e in elements)


def test_analyzer_extracts_class_methods_list(tmp_path: Path):
    f = tmp_path / "m.py"
    f.write_text(
        "class D:\n"
        "    def first(self): pass\n"
        "    def second(self): pass\n"
    )
    elements = PythonCodeAnalyzer(f).analyze()
    klass = next(e for e in elements if e.type == "class")
    assert "first" in klass.methods
    assert "second" in klass.methods


def test_analyzer_extracts_base_classes(tmp_path: Path):
    f = tmp_path / "m.py"
    f.write_text(
        "class Base: pass\n"
        "class Child(Base): pass\n"
    )
    elements = PythonCodeAnalyzer(f).analyze()
    child = next(e for e in elements if e.type == "class" and e.name == "Child")
    assert "Base" in child.base_classes


def test_analyzer_on_invalid_python_returns_empty(tmp_path: Path):
    f = tmp_path / "broken.py"
    f.write_text("def (oh no\n")
    elements = PythonCodeAnalyzer(f).analyze()
    assert elements == []


def test_analyzer_extracts_docstrings(tmp_path: Path):
    f = tmp_path / "m.py"
    f.write_text(
        'def documented():\n'
        '    """A docstring."""\n'
        '    return 1\n'
    )
    elements = PythonCodeAnalyzer(f).analyze()
    fn = next(e for e in elements if e.type == "function")
    assert fn.docstring == "A docstring."
