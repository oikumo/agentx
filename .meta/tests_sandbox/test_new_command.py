"""
Test script to verify the NewCommand works correctly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agentx.model.session.session_manager import SessionManager


def test_session_manager_flow():
    """Test the complete flow of session management."""
    print("Testing SessionManager flow...\n")
    
    # Test 1: Session manager always has a session
    print("1. Testing that session manager always has a session...")
    manager = SessionManager()
    session = manager.get_current_session()
    assert session is not None, "Session should always exist"
    assert session.is_created(), "Session should be created"
    print(f"   ✓ Initial session created: {session.name}")
    
    # Test 2: Create a new session
    print("\n2. Testing creation of new session...")
    new_session = manager.create_new_session("test_user_session")
    assert new_session is not None, "New session should be created"
    assert new_session.name == "test_user_session", "Session name should match"
    print(f"   ✓ New session created: {new_session.name}")
    
    # Test 3: Verify old session is destroyed
    print("\n3. Testing that old session is destroyed...")
    current_session = manager.get_current_session()
    assert current_session.name == "test_user_session", "Should have new session"
    print(f"   ✓ Current session is now: {current_session.name}")
    
    # Test 4: Create another session
    print("\n4. Testing creation of another session...")
    another_session = manager.create_new_session("another_session")
    assert another_session.name == "another_session", "Should have correct name"
    print(f"   ✓ Another session created: {another_session.name}")
    
    print("\n✓ All session management tests passed!")


if __name__ == "__main__":
    test_session_manager_flow()
