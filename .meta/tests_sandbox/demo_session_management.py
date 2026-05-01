"""
Demonstration of the session management system with backup functionality.

This script demonstrates:
1. A 'current' session always exists
2. When creating a new session with 'new', the current one is backed up with timestamp
3. Sessions are preserved on disk for data safety
"""
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agentx.model.session.session_manager import get_session_manager
from agentx.common.security import SESSION_DEFAULT_BASE_DIRECTORY


def demo():
    print("=" * 70)
    print("Session Management Demo: Always Current with Backup")
    print("=" * 70)
    
    # Get the session manager (creates 'current' session if needed)
    print("\n1. Getting session manager (creates 'current' session automatically)")
    manager = get_session_manager()
    session = manager.get_current_session()
    print(f"   ✓ Session name: {session.name}")
    print(f"   ✓ Session directory: {session.directory}")
    
    # Add some data to the session
    print("\n2. Adding data to current session")
    db = manager.get_database()
    if db:
        db.insert_history_entry("demo_command_1")
        db.insert_history_entry("demo_command_2")
        print("   ✓ Added 2 history entries")
    
    # Create a new session (simulating 'new' command)
    print("\n3. Creating new session (simulates 'new' command)")
    print("   → This will backup the current session with timestamp")
    new_session = manager.create_new_session("user_session")
    print(f"   ✓ New session name: {new_session.name}")
    print(f"   ✓ New session directory: {new_session.directory}")
    
    # Show backup directories
    print("\n4. Checking for backup directories")
    base_path = Path(SESSION_DEFAULT_BASE_DIRECTORY)
    backup_dirs = sorted([d for d in base_path.iterdir() 
                         if d.name.startswith("current_backup_")])
    print(f"   ✓ Found {len(backup_dirs)} backup(s)")
    if backup_dirs:
        print(f"   ✓ Latest backup: {backup_dirs[-1].name}")
    
    # Add more data to new session
    print("\n5. Adding data to new session")
    db = manager.get_database()
    if db:
        db.insert_history_entry("demo_command_3")
        print("   ✓ Added 1 more history entry")
    
    # Create another new session
    print("\n6. Creating another new session")
    another_session = manager.create_new_session("another_session")
    print(f"   ✓ Session name: {another_session.name}")
    print(f"   ✓ Session directory: {another_session.directory}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"✓ Current session: {manager.get_session_name()}")
    print(f"✓ Current directory: {manager.get_current_session().directory}")
    
    backup_dirs = sorted([d for d in base_path.iterdir() 
                         if d.name.startswith("current_backup_")])
    print(f"✓ Total backups created: {len(backup_dirs)}")
    print("\nKey Features:")
    print("  • 'current' session ALWAYS exists")
    print("  • Creating new session backs up current with timestamp")
    print("  • All sessions preserved on disk (never deleted)")
    print("=" * 70)


if __name__ == "__main__":
    demo()
