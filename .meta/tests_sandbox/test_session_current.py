"""
Test script to verify session management with backup functionality.
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agentx.model.session.session_manager import SessionManager, get_session_manager
from agentx.common.security import SESSION_DEFAULT_BASE_DIRECTORY


def test_session_always_exists():
    """Test that a 'current' session always exists."""
    print("\n=== Test 1: Session Always Exists ===")
    
    # Get session manager (should create 'current' session automatically)
    manager = get_session_manager()
    session = manager.get_current_session()
    
    assert session is not None, "Session should exist"
    assert session.is_created(), "Session should be created"
    assert session.name == "current", f"Session name should be 'current', got '{session.name}'"
    
    print(f"✓ Session name: {session.name}")
    print(f"✓ Session directory: {session.directory}")
    print(f"✓ Session exists: {session.is_created()}")
    return True


def test_new_session_creates_backup():
    """Test that creating a new session backs up the current one."""
    print("\n=== Test 2: New Session Creates Backup ===")
    
    manager = get_session_manager()
    initial_session = manager.get_current_session()
    initial_dir = initial_session.directory
    print(f"Initial session directory: {initial_dir}")
    
    # Add some data to the session
    db = manager.get_database()
    if db:
        db.insert_history_entry("test command 1")
        print("Added test data to session")
    
    # Create a new session (should backup the current one)
    print("\nCreating new session...")
    new_session = manager.create_new_session("test")
    
    assert new_session is not None, "New session should exist"
    assert new_session.name == "current", f"New session name should be 'current', got '{new_session.name}'"
    
    print(f"✓ New session name: {new_session.name}")
    print(f"✓ New session directory: {new_session.directory}")
    
    # Check if backup was created
    base_path = Path(SESSION_DEFAULT_BASE_DIRECTORY)
    backup_dirs = [d for d in base_path.iterdir() if d.name.startswith("current_backup_")]
    print(f"✓ Found {len(backup_dirs)} backup directory(ies)")
    
    if len(backup_dirs) > 0:
        print(f"✓ Backup exists: {backup_dirs[0]}")
        return True
    else:
        print("✗ No backup found!")
        return False


def test_multiple_new_sessions():
    """Test creating multiple new sessions."""
    print("\n=== Test 3: Multiple New Sessions ===")
    
    manager = get_session_manager()
    
    for i in range(3):
        print(f"\nCreating session iteration {i+1}...")
        session = manager.create_new_session(f"test_{i}")
        db = manager.get_database()
        if db:
            db.insert_history_entry(f"command_{i}")
        print(f"  Session: {session.name}, Directory: {session.directory}")
    
    # Count backups
    base_path = Path(SESSION_DEFAULT_BASE_DIRECTORY)
    backup_dirs = [d for d in base_path.iterdir() if d.name.startswith("current_backup_")]
    print(f"\n✓ Total backup directories: {len(backup_dirs)}")
    
    return len(backup_dirs) >= 2  # Should have at least 2 backups


def test_session_data_persistence():
    """Test that session data persists in backups."""
    print("\n=== Test 4: Session Data Persistence ===")
    
    manager = get_session_manager()
    
    # Get current session directory
    session = manager.get_current_session()
    if not session or not session.directory:
        print("✗ No current session")
        return False
    
    # Create a session with data
    db = manager.get_database()
    test_command = f"test_command_{Path(session.directory).name}"
    if db:
        db.insert_history_entry(test_command)
        print(f"Inserted: {test_command}")
    
    # Create new session
    manager.create_new_session("next")
    
    # Check backup directory for data
    base_path = Path(SESSION_DEFAULT_BASE_DIRECTORY)
    backup_dirs = sorted([d for d in base_path.iterdir() if d.name.startswith("current_backup_")])
    
    if backup_dirs:
        latest_backup = backup_dirs[-1]
        db_files = list(latest_backup.glob("*.db"))
        if db_files:
            print(f"✓ Backup database exists: {db_files[0].name}")
            return True
    
    print("✗ No backup database found")
    return False


def main():
    print("=" * 60)
    print("Session Management Test Suite")
    print("=" * 60)
    
    tests = [
        test_session_always_exists,
        test_new_session_creates_backup,
        test_multiple_new_sessions,
        test_session_data_persistence,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test.__name__, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
