#!/usr/bin/env python3
"""
Prompt Registry for KB MCP v4.

Manages registration and discovery of prompt templates.
"""

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class PromptArgument:
    """
    Definition of a prompt template argument.
    
    Attributes:
        name: Argument name (used in template as {{ name }})
        description: Human-readable description
        required: Whether argument must be provided
        default: Default value if not required
    """
    name: str
    description: str
    required: bool = False
    default: Any = None


@dataclass
class PromptInfo:
    """
    Metadata about a registered prompt.
    
    Attributes:
        name: Prompt identifier
        description: Human-readable description
        arguments: List of required/optional arguments
        category: Prompt category (onboarding, navigation, etc.)
    """
    name: str
    description: str
    arguments: list[PromptArgument] = field(default_factory=list)
    category: str = "general"


class PromptRegistry:
    """
    Registry for prompt templates.
    
    Manages registration, discovery, and retrieval of prompt templates.
    Uses a simple dictionary-based storage with category indexing.
    
    Example:
        registry = PromptRegistry()
        registry.register(
            name="onboard-agent",
            description="I'm new to this project. Explain it to me.",
            template="...",
            arguments=[]
        )
    """
    
    def __init__(self):
        """Initialize an empty prompt registry."""
        self._prompts: dict[str, dict[str, Any]] = {}
        self._categories: dict[str, set[str]] = {}
    
    def register(
        self,
        name: str,
        description: str,
        template: str,
        arguments: list[PromptArgument] | None = None,
        category: str = "general",
    ) -> None:
        """
        Register a prompt template.
        
        Args:
            name: Unique prompt identifier
            description: Human-readable description
            template: Jinja2 template string
            arguments: List of prompt arguments
            category: Category for grouping (onboarding, navigation, etc.)
            
        Raises:
            ValueError: If prompt name already exists
        """
        if name in self._prompts:
            raise ValueError(f"Prompt '{name}' already registered")
        
        self._prompts[name] = {
            "name": name,
            "description": description,
            "template": template,
            "arguments": arguments or [],
            "category": category,
        }
        
        # Index by category
        if category not in self._categories:
            self._categories[category] = set()
        self._categories[category].add(name)
    
    def get(self, name: str) -> dict[str, Any] | None:
        """
        Get a prompt template by name.
        
        Args:
            name: Prompt identifier
            
        Returns:
            Prompt metadata dict or None if not found
        """
        return self._prompts.get(name)
    
    def list_prompts(self, category: str | None = None) -> list[PromptInfo]:
        """
        List all registered prompts.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of prompt info objects
        """
        if category:
            names = self._categories.get(category, set())
        else:
            names = set(self._prompts.keys())
        
        return [
            PromptInfo(
                name=name,
                description=self._prompts[name]["description"],
                arguments=self._prompts[name]["arguments"],
                category=self._prompts[name]["category"],
            )
            for name in sorted(names)
        ]
    
    def list_categories(self) -> list[str]:
        """
        Get all registered categories.
        
        Returns:
            List of category names
        """
        return sorted(self._categories.keys())
    
    def get_template(self, name: str) -> str | None:
        """
        Get the raw template string for a prompt.
        
        Args:
            name: Prompt identifier
            
        Returns:
            Template string or None if not found
        """
        prompt = self._prompts.get(name)
        return prompt["template"] if prompt else None
    
    def has_prompt(self, name: str) -> bool:
        """
        Check if a prompt exists.
        
        Args:
            name: Prompt identifier
            
        Returns:
            True if prompt exists
        """
        return name in self._prompts