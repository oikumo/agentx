#!/usr/bin/env python3
"""
Command-line interface for KB operations.

This provides user-triggered commands for KB management.
"""

import sys
from pathlib import Path

# Ensure we can import from parent
sys.path.insert(0, str(Path(__file__).parent))

from meta_tools import kb_clean_and_populate as _kb_clean_populate


def kb_clean_and_populate_command(kb: str = "both", verbose: bool = True):
    """
    Command to clean and populate KB databases.
    
    Usage:
        python .meta.tools/commands.py kb_clean_and_populate both
        python .meta.tools/commands.py kb_clean_and_populate meta
        python .meta.tools/commands.py kb_clean_and_populate agentx
    """
    result = _kb_clean_populate(kb=kb, verbose=verbose)
    print(result)
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="KB Management Commands")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # kb_clean_and_populate command
    kb_parser = subparsers.add_parser("kb_clean_and_populate", help="Clean and populate KB")
    kb_parser.add_argument("--kb", choices=["meta", "agentx", "both"], default="both",
                          help="Which KB to populate")
    kb_parser.add_argument("--verbose", action="store_true", default=True,
                          help="Print progress")
    
    args = parser.parse_args()
    
    if args.command == "kb_clean_and_populate":
        kb_clean_and_populate_command(kb=args.kb, verbose=args.verbose)
    else:
        parser.print_help()
