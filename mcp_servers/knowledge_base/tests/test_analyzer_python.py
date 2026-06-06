#!/usr/bin/env python3
"""
Unit tests for Python AST Analyzer.
"""

import pytest
import tempfile
from pathlib import Path

from analyzer.python_ast import PythonASTAnalyzer
from graph.models import EntityKind, RelationshipKind


class TestPythonASTAnalyzer:
    """Tests for Python AST analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return PythonASTAnalyzer()
    
    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary Python project for testing."""
        # Create directory structure
        src_dir = tmp_path / "src" / "mypackage"
        src_dir.mkdir(parents=True)
        
        # Create a simple module with class and function
        module_py = src_dir / "module.py"
        module_py.write_text("""
\"\"\"Sample module for testing.\"\"\"

class BaseClass:
    \"\"\"Base class for testing.\"\"\"
    pass

class MyClass(BaseClass):
    \"\"\"
    A sample class.
    
    :param name: The name
    :returns: Nothing
    \"\"\"
    
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        \"\"\"Say hello.\"\"\"
        return f"Hello, {self.name}"
    
    def call_other(self):
        \"\"\"Call another method.\"\"\"
        return self.greet()

def helper_function(x, y):
    \"\"\"
    Helper function.
    
    :param x: First value
    :param y: Second value
    :returns: Sum of x and y
    \"\"\"
    return x + y

async def async_function():
    \"\"\"Async function.\"\"\"
    return await something()

# Decorator test
@property
def my_property():
    pass

@staticmethod
def static_method():
    pass
""")
        
        # Create another module that imports
        other_py = src_dir / "other.py"
        other_py.write_text("""
from module import MyClass, helper_function

import os
import sys

class Consumer:
    \"\"\"Class that uses imported items.\"\"\"
    
    def __init__(self):
        self.obj = MyClass("test")
    
    def use_helper(self):
        return helper_function(1, 2)
""")
        
        return tmp_path
    
    def test_supported_extensions(self, analyzer):
        """Test supported file extensions."""
        assert '.py' in analyzer.supported_extensions
        assert '.pyi' in analyzer.supported_extensions
    
    def test_language_name(self, analyzer):
        """Test language name."""
        assert analyzer.language_name == 'python'
    
    def test_confidence(self, analyzer):
        """Test confidence score."""
        assert analyzer.confidence == 0.95
    
    def test_is_supported_file(self, analyzer):
        """Test file support check."""
        assert analyzer.is_supported_file(Path("test.py"))
        assert analyzer.is_supported_file(Path("test.pyi"))
        assert not analyzer.is_supported_file(Path("test.js"))
        assert not analyzer.is_supported_file(Path("test.txt"))
    
    def test_analyze_file_basic(self, analyzer, temp_project):
        """Test basic file analysis."""
        module_py = temp_project / "src" / "mypackage" / "module.py"
        
        entities, relationships = analyzer.analyze_file(module_py)
        
        # Should find classes and functions
        assert len(entities) > 0
        
        # Find specific entities
        class_names = [e.name for e in entities if e.kind == EntityKind.CLASS]
        func_names = [e.name for e in entities if e.kind == EntityKind.FUNCTION]
        method_names = [e.name for e in entities if e.kind == EntityKind.METHOD]
        
        assert "BaseClass" in class_names
        assert "MyClass" in class_names
        assert "helper_function" in func_names
        assert "async_function" in func_names
        assert "greet" in method_names
        assert "call_other" in method_names
    
    def test_extract_class_with_inheritance(self, analyzer, temp_project):
        """Test class extraction with inheritance."""
        module_py = temp_project / "src" / "mypackage" / "module.py"
        
        entities, relationships = analyzer.analyze_file(module_py)
        
        # Find MyClass
        my_class = next((e for e in entities if e.name == "MyClass"), None)
        assert my_class is not None
        
        # Check inheritance relationship
        extends_rels = [r for r in relationships if r.kind == RelationshipKind.EXTENDS]
        assert len(extends_rels) > 0
    
    def test_extract_docstring(self, analyzer, temp_project):
        """Test docstring extraction."""
        module_py = temp_project / "src" / "mypackage" / "module.py"
        
        entities, _ = analyzer.analyze_file(module_py)
        
        # Find MyClass
        my_class = next((e for e in entities if e.name == "MyClass"), None)
        assert my_class is not None
        assert my_class.docstring is not None
        assert "sample class" in my_class.docstring.summary.lower()
    
    def test_extract_decorators(self, analyzer, temp_project):
        """Test decorator extraction."""
        module_py = temp_project / "src" / "mypackage" / "module.py"
        
        entities, relationships = analyzer.analyze_file(module_py)
        
        # Check that decorators are in metadata
        for entity in entities:
            if entity.metadata.get("decorators"):
                assert len(entity.metadata["decorators"]) > 0
    
    def test_detect_patterns(self, analyzer, temp_project):
        """Test design pattern detection."""
        module_py = temp_project / "src" / "mypackage" / "module.py"
        
        entities, _ = analyzer.analyze_file(module_py)
        
        # Check for pattern detection
        for entity in entities:
            if entity.metadata.get("pattern"):
                assert isinstance(entity.metadata["pattern"], list)
    
    def test_infer_layer(self, analyzer, temp_project):
        """Test architecture layer inference."""
        module_py = temp_project / "src" / "mypackage" / "module.py"
        
        entities, _ = analyzer.analyze_file(module_py)
        
        # Check that layers are inferred
        for entity in entities:
            assert "layer" in entity.metadata
            assert entity.metadata["layer"] in ['model', 'view', 'controller', 'service', 'repository', 'test', 'unknown']
    
    def test_extract_calls(self, analyzer, temp_project):
        """Test call relationship extraction."""
        module_py = temp_project / "src" / "mypackage" / "module.py"
        
        entities, relationships = analyzer.analyze_file(module_py)
        
        # Find call relationships
        call_rels = [r for r in relationships if r.kind == RelationshipKind.CALLS]
        
        # Should find at least one call (call_other calls greet)
        assert len(call_rels) > 0
    
    def test_extract_imports(self, analyzer, temp_project):
        """Test import extraction."""
        other_py = temp_project / "src" / "mypackage" / "other.py"
        
        entities, relationships = analyzer.analyze_file(other_py)
        
        # Should find import entities
        import_entities = [e for e in entities if e.kind == EntityKind.MODULE and 'import' in e.id]
        assert len(import_entities) > 0
    
    def test_analyze_project(self, analyzer, temp_project):
        """Test full project analysis."""
        all_entities, all_relationships = analyzer.analyze_project(
            temp_project,
            exclude_dirs={'venv', '.git', '__pycache__'},
        )
        
        # Should find entities from both modules
        assert len(all_entities) > 5
        
        # Should find relationships
        assert len(all_relationships) > 0
    
    def test_get_config_files(self, analyzer, temp_project):
        """Test config file detection."""
        # Create a config file
        (temp_project / "pyproject.toml").write_text("[project]\nname = 'test'")
        
        configs = analyzer.get_config_files(temp_project)
        
        assert len(configs) > 0
        assert any("pyproject.toml" in str(c) for c in configs)
    
    def test_async_function_detection(self, analyzer, temp_project):
        """Test async function detection."""
        module_py = temp_project / "src" / "mypackage" / "module.py"
        
        entities, _ = analyzer.analyze_file(module_py)
        
        # Find async function
        async_func = next((e for e in entities if e.name == "async_function"), None)
        assert async_func is not None
        assert async_func.metadata.get("is_async") is True
    
    def test_method_vs_function(self, analyzer, temp_project):
        """Test method vs function distinction."""
        module_py = temp_project / "src" / "mypackage" / "module.py"
        
        entities, _ = analyzer.analyze_file(module_py)
        
        # Methods should have class in metadata
        methods = [e for e in entities if e.kind == EntityKind.METHOD]
        for method in methods:
            assert "class" in method.metadata
            assert method.metadata["class"] == "MyClass"
        
        # Functions should not have class
        functions = [e for e in entities if e.kind == EntityKind.FUNCTION]
        for func in functions:
            assert "class" not in func.metadata or func.metadata.get("class") is None
    
    def test_syntax_error_handling(self, analyzer, tmp_path):
        """Test handling of syntax errors."""
        bad_py = tmp_path / "bad.py"
        bad_py.write_text("def broken(")  # Syntax error
        
        with pytest.raises(SyntaxError):
            analyzer.analyze_file(bad_py)
    
    def test_file_not_found(self, analyzer):
        """Test handling of missing files."""
        with pytest.raises(FileNotFoundError):
            analyzer.analyze_file(Path("/nonexistent/file.py"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
