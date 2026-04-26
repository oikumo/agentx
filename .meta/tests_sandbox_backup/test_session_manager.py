"""
Test suite for SessionManager.

Tests ensure:
1. A session always exists
2. New sessions can be created
3. Session manager is a singleton
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agentx.model.session.session_manager import SessionManager, get_session_manager


def test_session_manager_always_has_session():
    """Test that session manager always has a current session."""
    manager = SessionManager()
    session = manager.get_current_session()
    
    assert session is not None, "Session should always exist"
    assert session.is_created(), "Session should be created"
    print("✓ Session manager always has a session")


def test_session_manager_singleton():
    """Test that session manager is a singleton."""
    manager1 = SessionManager()
    manager2 = SessionManager()
    
    assert manager1 is manager2, "SessionManager should be a singleton"
    print("✓ SessionManager is a singleton")


def test_create_new_session():
    """Test creating a new session."""
    manager = SessionManager()
    old_session_name = manager.get_session_name()
    
    new_session = manager.create_new_session("test_session")
    
    assert new_session is not None, "New session should be created"
    assert new_session.name == "test_session", "Session name should match"
    assert new_session.is_created(), "New session should be created"
    print(f"✓ Created new session: {new_session.name}")


def test_get_session_name():
    """Test getting session name."""
    manager = SessionManager()
    name = manager.get_session_name()
    
    assert name is not None, "Session name should not be None"
    assert isinstance(name, str), "Session name should be a string"
    print(f"✓ Session name: {name}")


def test_has_session():
    """Test checking if session exists."""
    manager = SessionManager()
    
    assert manager.has_session(), "Should have a session"
    print("✓ has_session() returns True")


def test_get_database():
    """Test getting database for current session."""
    manager = SessionManager()
    database = manager.get_database()
    
    assert database is not None, "Database should exist"
    print("✓ Database exists for current session")


if __name__ == "__main__":
    print("Testing SessionManager...\n")
    
    test_session_manager_always_has_session()
    test_session_manager_singleton()
    test_create_new_session()
    test_get_session_name()
    test_has_session()
    test_get_database()
    
    print("\n✓ All tests passed!")
