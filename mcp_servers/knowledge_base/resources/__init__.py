#!/usr/bin/env python3
"""
MCP Resources Layer for KB MCP v4.

Exposes project knowledge as a virtual filesystem via knowledge-base:// scheme.
"""

from .registry import ResourceHandler, ResourceRegistry
from .project import ProjectResources
from .arch import ArchitectureResources
from .flows import FlowResources
from .api import APIResources
from .code import CodeResources
from .session import SessionResources
from .quality import QualityResources

__all__ = [
    "ResourceHandler",
    "ResourceRegistry",
    "ProjectResources",
    "ArchitectureResources",
    "FlowResources",
    "APIResources",
    "CodeResources",
    "SessionResources",
    "QualityResources",
]