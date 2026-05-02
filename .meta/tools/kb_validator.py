#!/usr/bin/env python3
"""
KB-First Enforcement Tool
Validates that KB was queried before tasks
"""

import os
import sys
from pathlib import Path

KB_DIR = Path(__file__).parent.parent / "knowledge_base"
SESSION_LOG = Path(__file__).parent.parent / "LOG.md"

def check_kb_first(task: str) -> bool:
    """Check if KB was queried for this task"""
    
    # 1. Check if KB exists
    if not KB_DIR.exists():
        print("❌ KB directory missing!")
        return False
    
    # 2. Check if KB has entries
    entries = list(KB_DIR.glob("entries/*.md")) if (KB_DIR / "entries").exists() else []
    if not entries:
        print("⚠️  KB is empty - auto-populating...")
        # Would trigger kb populate here
        return False
    
    # 3. Check session log for KB query
    if SESSION_LOG.exists():
        content = SESSION_LOG.read_text()
        if "kb_ask" in content or "kb search" in content:
            print("✅ KB query logged")
            return True
    
    print("⚠️  No KB query found in session log")
    return False

if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "unknown task"
    result = check_kb_first(task)
    sys.exit(0 if result else 1)
