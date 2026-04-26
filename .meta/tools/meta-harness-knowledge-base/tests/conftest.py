#!/usr/bin/env python3
"""
Test configuration for knowledge base tests.
"""

import os
import tempfile
import sqlite3
from pathlib import Path
import sys

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set up test database configuration
def pytest_configure(config):
    """Set up test configuration."""
    pass

def pytest_unconfigure(config):
    """Clean up test configuration."""
    pass