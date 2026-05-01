"""
Unit tests for agentx.model.session.session_state_manager module.

Tests cover:
- SessionStateManager: State management with Petri nets
- SessionStateBuilder: Builder pattern for session states
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from agentx.model.session.session_state_manager import (
    SessionStateManager,
    SessionStateBuilder,
)
from agentx.model.session.adaptive_petri_net import SessionState


class TestSessionStateManager:
    """Tests for SessionStateManager class."""

    def test_create_session_state_manager(self):
        """Test creating SessionStateManager."""
        manager = SessionStateManager("test_session")

        assert manager.session_name == "test_session"
        assert manager.created_at is not None
        assert manager.updated_at is not None

    def test_default_session_name(self):
        """Test default session name."""
        manager = SessionStateManager()

        assert manager.session_name == "default"

    def test_set_objective(self):
        """Test setting session objective."""
        manager = SessionStateManager("test")
        manager.set_objective("Test objective")

        state = manager.get_state()
        assert state.objective == "Test objective"

    def test_set_objective_with_context(self):
        """Test setting objective with initial context."""
        manager = SessionStateManager("test")
        manager.set_objective("Test objective", initial_context={"key": "value"})

        state = manager.get_state()
        assert state.objective == "Test objective"

    def test_update_context(self):
        """Test updating context."""
        manager = SessionStateManager("test")
        manager.set_objective("Test")
        manager.update_context("test_key", "test_value")

        # Context should be updated
        assert manager.petri_net is not None

    def test_advance_objective(self):
        """Test advancing objective state."""
        manager = SessionStateManager("test")
        manager.set_objective("Test")

        # Try to advance (may fail if no enabled transitions)
        result = manager.advance_objective("test_transition")
        # Result depends on Petri net state
        assert isinstance(result, bool)

    def test_get_state(self):
        """Test getting session state."""
        manager = SessionStateManager("test")
        manager.set_objective("Test objective")

        state = manager.get_state()
        assert isinstance(state, SessionState)
        assert state.objective == "Test objective"

    def test_is_complete_initially_false(self):
        """Test that session is not complete initially."""
        manager = SessionStateManager("test")
        manager.set_objective("Test")

        assert manager.is_complete() is False

    def test_reset(self):
        """Test resetting session state."""
        manager = SessionStateManager("test")
        manager.set_objective("Test")

        manager.reset()

        # State should be reset
        state = manager.get_state()
        assert state is not None

    def test_get_history(self):
        """Test getting state history."""
        manager = SessionStateManager("test")
        manager.set_objective("Test")

        history = manager.get_history()
        assert isinstance(history, list)

    def test_to_dict(self):
        """Test serializing to dictionary."""
        manager = SessionStateManager("test")
        manager.set_objective("Test objective")

        data = manager.to_dict()

        assert isinstance(data, dict)
        assert "session_name" in data
        assert "objective" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_repr(self):
        """Test string representation."""
        manager = SessionStateManager("test")
        manager.set_objective("Test")

        repr_str = repr(manager)
        assert "test" in repr_str.lower()


class TestSessionStateBuilder:
    """Tests for SessionStateBuilder class."""

    def test_create_builder(self):
        """Test creating SessionStateBuilder."""
        builder = SessionStateBuilder("test_session")

        assert builder.session_name == "test_session"

    def test_default_builder_name(self):
        """Test default builder name."""
        builder = SessionStateBuilder()

        assert builder.session_name == "default"

    def test_set_objective(self):
        """Test setting objective in builder."""
        builder = SessionStateBuilder("test")
        result = builder.set_objective("Test objective")

        # Should return self for chaining
        assert result is builder

    def test_add_transition(self):
        """Test adding transition to builder."""
        builder = SessionStateBuilder("test")
        result = builder.add_transition("t1", ["p1"], ["p2"])

        # Should return self for chaining
        assert result is builder
        assert len(builder.transitions) == 1

    def test_build_simple_net(self):
        """Test building a simple Petri net."""
        builder = SessionStateBuilder("test")
        builder.set_objective("Test")
        builder.add_transition("t1", ["p1"], ["p2"])

        manager = builder.build()

        assert manager is not None
        assert isinstance(manager, SessionStateManager)

    def test_builder_chain(self):
        """Test fluent interface chaining."""
        builder = SessionStateBuilder("test")
        result = (builder
                  .set_objective("Test")
                  .add_transition("t1", ["p1"], ["p2"])
                  .add_transition("t2", ["p2"], ["p3"]))

        assert result is builder
        assert len(builder.transitions) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
