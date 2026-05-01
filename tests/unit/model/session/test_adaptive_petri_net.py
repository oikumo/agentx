"""
Unit tests for agentx.model.session.adaptive_petri_net module.

Tests cover:
- Place: Token storage and management
- Transition: Firing logic and arc management
- AdaptivePetriNet: Net construction and state management
- SessionState: State representation
"""

import pytest
from agentx.model.session.adaptive_petri_net import (
    Place,
    Transition,
    AdaptivePetriNet,
    SessionState,
    AdaptivePetriNetConfig,
)


class TestPlace:
    """Tests for Place class."""

    def test_create_place_default_tokens(self):
        """Test creating a place with default 0 tokens."""
        place = Place("test_place")
        assert place.name == "test_place"
        assert place.tokens == 0

    def test_create_place_with_tokens(self):
        """Test creating a place with initial tokens."""
        place = Place("test_place", tokens=5)
        assert place.tokens == 5

    def test_negative_tokens_raises_error(self):
        """Test that negative tokens raise ValueError."""
        with pytest.raises(ValueError, match="Token count cannot be negative"):
            Place("invalid_place", tokens=-1)

    def test_place_repr(self):
        """Test string representation of Place."""
        place = Place("test", tokens=3)
        assert "test" in repr(place)
        assert "3" in repr(place)


class TestTransition:
    """Tests for Transition class."""

    def test_create_transition(self):
        """Test creating a transition."""
        transition = Transition("test_transition")
        assert transition.name == "test_transition"
        assert len(transition.inputs) == 0
        assert len(transition.outputs) == 0

    def test_add_input_arc(self):
        """Test adding input arc."""
        transition = Transition("t1")
        place = Place("p1", tokens=1)
        transition.add_input(place, weight=1)
        assert place in transition.inputs
        assert transition.inputs[place] == 1

    def test_add_output_arc(self):
        """Test adding output arc."""
        transition = Transition("t1")
        place = Place("p1")
        transition.add_output(place, weight=1)
        assert place in transition.outputs
        assert transition.outputs[place] == 1

    def test_is_enabled_no_inputs(self):
        """Test transition with no inputs is enabled."""
        transition = Transition("t1")
        assert transition.is_enabled() is True

    def test_is_enabled_with_tokens(self):
        """Test transition is enabled when input places have tokens."""
        transition = Transition("t1")
        place = Place("p1", tokens=2)
        transition.add_input(place, weight=1)
        assert transition.is_enabled() is True

    def test_is_enabled_without_tokens(self):
        """Test transition is disabled when input places lack tokens."""
        transition = Transition("t1")
        place = Place("p1", tokens=0)
        transition.add_input(place, weight=1)
        assert transition.is_enabled() is False

    def test_fire_success(self):
        """Test successful transition firing."""
        transition = Transition("t1")
        input_place = Place("p1", tokens=2)
        output_place = Place("p2", tokens=0)

        transition.add_input(input_place, weight=1)
        transition.add_output(output_place, weight=1)

        assert transition.is_enabled() is True
        result = transition.fire()

        assert result is True
        assert input_place.tokens == 1
        assert output_place.tokens == 1

    def test_fire_disabled(self):
        """Test firing disabled transition fails."""
        transition = Transition("t1")
        place = Place("p1", tokens=0)
        transition.add_input(place, weight=1)

        assert transition.is_enabled() is False
        result = transition.fire()
        assert result is False

    def test_transition_repr(self):
        """Test string representation of Transition."""
        transition = Transition("test")
        assert "test" in repr(transition)


class TestAdaptivePetriNet:
    """Tests for AdaptivePetriNet class."""

    def test_create_net(self):
        """Test creating a Petri net."""
        net = AdaptivePetriNet("test_net")
        assert net.name == "test_net"
        assert len(net.places) == 0
        assert len(net.transitions) == 0
        assert net.objective is None

    def test_add_place(self):
        """Test adding a place to the net."""
        net = AdaptivePetriNet()
        place = net.add_place("p1", tokens=2)
        assert "p1" in net.places
        assert net.places["p1"].tokens == 2
        assert place is net.places["p1"]

    def test_add_duplicate_place(self):
        """Test adding duplicate place returns existing."""
        net = AdaptivePetriNet()
        place1 = net.add_place("p1", tokens=1)
        place2 = net.add_place("p1", tokens=2)
        assert place1 is place2
        assert net.places["p1"].tokens == 1

    def test_add_transition(self):
        """Test adding a transition to the net."""
        net = AdaptivePetriNet()
        transition = net.add_transition("t1")
        assert "t1" in net.transitions
        assert transition.name == "t1"

    def test_add_arc_place_to_transition(self):
        """Test adding arc from place to transition."""
        net = AdaptivePetriNet()
        place = net.add_place("p1")
        transition = net.add_transition("t1")
        net.add_arc(place, transition, weight=1)
        assert place in transition.inputs

    def test_add_arc_transition_to_place(self):
        """Test adding arc from transition to place."""
        net = AdaptivePetriNet()
        place = net.add_place("p1")
        transition = net.add_transition("t1")
        net.add_arc(transition, place, weight=1)
        assert place in transition.outputs

    def test_add_arc_invalid_connection(self):
        """Test adding invalid arc raises error."""
        net = AdaptivePetriNet()
        place1 = net.add_place("p1")
        place2 = net.add_place("p2")

        with pytest.raises(ValueError):
            net.add_arc(place1, place2)

    def test_set_objective(self):
        """Test setting objective initializes net."""
        net = AdaptivePetriNet()
        net.set_objective("Test objective")

        assert net.objective == "Test objective"
        assert "objective_pending" in net.places
        assert net.places["objective_pending"].tokens == 1
        assert "objective_in_progress" in net.places
        assert "objective_completed" in net.places

    def test_fire_transition_success(self):
        """Test firing a transition in the net."""
        net = AdaptivePetriNet()
        net.set_objective("Test")

        # Create a simple enabled transition
        place = net.add_place("p1", tokens=1)
        transition = net.add_transition("t1")
        net.add_arc(place, transition)

        result = net.fire_transition("t1")
        assert result is True

    def test_fire_nonexistent_transition(self):
        """Test firing non-existent transition fails."""
        net = AdaptivePetriNet()
        result = net.fire_transition("nonexistent")
        assert result is False

    def test_marking(self):
        """Test getting current marking."""
        net = AdaptivePetriNet()
        net.add_place("p1", tokens=2)
        net.add_place("p2", tokens=3)

        marking = net.marking()
        assert marking["p1"] == 2
        assert marking["p2"] == 3

    def test_enabled_transitions(self):
        """Test getting enabled transitions."""
        net = AdaptivePetriNet()
        place = net.add_place("p1", tokens=1)

        t1 = net.add_transition("t1")
        t2 = net.add_transition("t2")

        net.add_arc(place, t1)
        net.add_arc(place, t2)

        enabled = net.enabled_transitions()
        assert len(enabled) == 2

    def test_get_state(self):
        """Test extracting session state from net."""
        net = AdaptivePetriNet()
        net.set_objective("Test objective")

        state = net.get_state()
        assert isinstance(state, SessionState)
        assert state.objective == "Test objective"
        assert "marking" in state.context
        assert "objective_status" in state.context

    def test_is_complete(self):
        """Test checking if net is complete."""
        net = AdaptivePetriNet()
        assert net.is_complete() is False

        completed_place = net.add_place("objective_completed", tokens=1)
        assert net.is_complete() is True

    def test_reset(self):
        """Test resetting the net."""
        net = AdaptivePetriNet()
        net.set_objective("Test")
        net.add_place("p1", tokens=5)
        net.fire_transition("objective_pending")  # Fire to change state

        net.reset()

        assert net.objective is None
        assert net.places["p1"].tokens == 0
        assert len(net.state_history) == 0

    def test_state_history(self):
        """Test that setting objective creates initial state history."""
        net = AdaptivePetriNet()
        net.set_objective("Test")

        # Setting objective should create initial state
        assert len(net.state_history) >= 1
        
        # Verify the history contains the objective
        if len(net.state_history) > 0:
            assert net.state_history[0]["objective"] == "Test"


class TestSessionState:
    """Tests for SessionState dataclass."""

    def test_create_default_state(self):
        """Test creating default session state."""
        state = SessionState()
        assert state.objective == ""
        assert state.context == {}
        assert state.created_at == ""
        assert state.updated_at == ""

    def test_create_state_with_values(self):
        """Test creating session state with values."""
        context = {"key": "value"}
        state = SessionState(
            objective="Test",
            context=context,
            created_at="2024-01-01",
            updated_at="2024-01-02"
        )
        assert state.objective == "Test"
        assert state.context == context
        assert state.created_at == "2024-01-01"
        assert state.updated_at == "2024-01-02"


class TestAdaptivePetriNetConfig:
    """Tests for AdaptivePetriNetConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = AdaptivePetriNetConfig()
        assert config.auto_save is True
        assert config.max_history == 100
        assert config.enable_adaptation is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = AdaptivePetriNetConfig(
            auto_save=False,
            max_history=50,
            enable_adaptation=False
        )
        assert config.auto_save is False
        assert config.max_history == 50
        assert config.enable_adaptation is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
