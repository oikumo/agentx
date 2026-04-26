#!/usr/bin/env python3
"""
Simple KB Population Command

Usage:
    python .meta/tools/populate.py [both|meta|agentx]
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from meta.tools.populate_kb import KBPopulator


def main():
    """Main entry point."""
    # Get KB target from args (default: both)
    target = sys.argv[1] if len(sys.argv) > 1 else "both"
    
    if target not in ["both", "meta", "agentx"]:
        print("Usage: python .meta/tools/populate.py [both|meta|agentx]")
        print(f"  both    - Populate both KBs (default)")
        print(f"  meta    - Populate only Meta Harness KB")
        print(f"  agentx  - Populate only Agent-X KB")
        sys.exit(1)
    
    # Run population
    populator = KBPopulator(target_kb=target, verbose=True)
    populator.populate()


if __name__ == "__main__":
    main()
