#!/usr/bin/env python3
"""
MCP Prompts Layer for KB MCP v4.

Provides pre-built prompt templates that guide agents through common tasks.
"""

from .engine import PromptEngine
from .registry import PromptRegistry, PromptInfo, PromptArgument

__all__ = [
    "PromptEngine",
    "PromptRegistry",
    "PromptInfo",
    "PromptArgument",
]