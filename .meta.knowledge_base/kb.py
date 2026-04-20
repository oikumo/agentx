#!/usr/bin/env python3
"""
Knowledge Base CLI - Wrapper for CLI module.
"""
import sys
from pathlib import Path

# Ensure core is importable
sys.path.insert(0, str(Path(__file__).parent))

from cli import main as cli_main

if __name__ == '__main__':
    cli_main()
