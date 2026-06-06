#!/usr/bin/env python3
"""
Abstract base class for language backends in KB MCP v4.

All language analyzers must implement this interface.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from graph.models import Entity, Relationship


class LanguageBackend(ABC):
    """
    Abstract base class for language-specific code analyzers.
    
    Each backend is responsible for:
    - Parsing source files in its language
    - Extracting entities (classes, functions, etc.)
    - Detecting relationships between entities
    - Providing language-specific metadata
    
    Backends can use AST parsers, tree-sitter, LSP, or regex heuristics.
    """
    
    @property
    @abstractmethod
    def supported_extensions(self) -> set[str]:
        """
        Get file extensions supported by this backend.
        
        Returns:
            Set of extensions (e.g., {'.py', '.pyi'})
        """
        pass
    
    @property
    @abstractmethod
    def language_name(self) -> str:
        """
        Get the name of the language this backend analyzes.
        
        Returns:
            Language name (e.g., 'python', 'typescript')
        """
        pass
    
    @abstractmethod
    def analyze_file(self, path: Path) -> tuple[list[Entity], list[Relationship]]:
        """
        Analyze a single source file.
        
        Args:
            path: Path to the source file
            
        Returns:
            Tuple of (entities, relationships) extracted from the file
            
        Raises:
            SyntaxError: If file has syntax errors
            FileNotFoundError: If file doesn't exist
        """
        pass
    
    @abstractmethod
    def analyze_project(self, root: Path, exclude_dirs: set[str] | None = None) -> tuple[list[Entity], list[Relationship]]:
        """
        Analyze all supported files in a project.
        
        Args:
            root: Root directory of the project
            exclude_dirs: Set of directory names to exclude (e.g., {'venv', '.git'})
            
        Returns:
            Tuple of (all_entities, all_relationships) for the project
        """
        pass
    
    @property
    def confidence(self) -> float:
        """
        Get confidence score for this backend's analysis.
        
        Returns:
            Confidence between 0.0 and 1.0
            1.0 = AST-level certainty
            0.5 = Heuristic/regrex-based
        """
        return 1.0  # Default: high confidence for AST-based
    
    def is_supported_file(self, path: Path) -> bool:
        """
        Check if a file is supported by this backend.
        
        Args:
            path: Path to check
            
        Returns:
            True if file extension is supported
        """
        return path.suffix.lower() in self.supported_extensions
    
    def get_config_files(self, root: Path) -> list[Path]:
        """
        Get language-specific configuration files.
        
        Args:
            root: Project root directory
            
        Returns:
            List of config file paths
        """
        # Default: no config files
        return []
    
    def extract_metadata(self, path: Path) -> dict[str, Any]:
        """
        Extract additional metadata from a file.
        
        Args:
            path: Path to the file
            
        Returns:
            Dictionary of metadata (e.g., git info, complexity)
        """
        # Default: empty metadata
        return {}