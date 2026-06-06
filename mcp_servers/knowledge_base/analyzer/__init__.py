#!/usr/bin/env python3
"""
Analyzer package for KB MCP v4.

Provides semantic code analysis for multiple languages.
"""

from .base import LanguageBackend
from .python_ast import PythonASTAnalyzer

__all__ = [
    "LanguageBackend",
    "PythonASTAnalyzer",
]

__version__ = "4.0.0"
