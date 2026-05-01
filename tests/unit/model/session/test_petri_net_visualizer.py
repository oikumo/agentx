"""
Unit tests for agentx.model.session.petri_net_visualizer module.

Tests cover:
- PetriNetVisualizer: ASCII art visualization
- Flow diagram generation
- Marking and enabled transition strings
"""

import pytest
from unittest.mock import patch, MagicMock

from agentx.model.session.petri_net_visualizer import (
    PetriNetVisualizer,
    print_petri_net,
)
from agentx.model.session.adaptive_petri_net import AdaptivePetriNet


class TestPetriNetVisualizer:
    """Tests for PetriNetVisualizer class."""

    def test_create_visualizer(self):
        """Test creating PetriNetVisualizer."""
        petri_net = AdaptivePetriNet("test_net")
        visualizer = PetriNetVisualizer(petri_net)

        assert visualizer.petri_net is petri_net

    def test_to_ascii_basic(self):
        """Test basic ASCII art generation."""
        petri_net = AdaptivePetriNet("test")
        visualizer = PetriNetVisualizer(petri_net)

        ascii_art = visualizer.to_ascii()

        assert isinstance(ascii_art, str)
        assert len(ascii_art) > 0
        assert "test" in ascii_art

    def test_to_ascii_with_objective(self):
        """Test ASCII art with objective."""
        petri_net = AdaptivePetriNet("test")
        petri_net.set_objective("Test objective")
        visualizer = PetriNetVisualizer(petri_net)

        ascii_art = visualizer.to_ascii()

        assert "Test objective" in ascii_art

    def test_to_ascii_with_places(self):
        """Test ASCII art shows places."""
        petri_net = AdaptivePetriNet("test")
        petri_net.add_place("p1", tokens=1)
        petri_net.add_place("p2", tokens=0)
        visualizer = PetriNetVisualizer(petri_net)

        ascii_art = visualizer.to_ascii()

        assert "p1" in ascii_art
        assert "p2" in ascii_art
        # p1 has tokens, should show filled
        assert "●" in ascii_art or "○" in ascii_art

    def test_to_ascii_with_transitions(self):
        """Test ASCII art shows transitions."""
        petri_net = AdaptivePetriNet("test")
        petri_net.add_transition("t1")
        visualizer = PetriNetVisualizer(petri_net)

        ascii_art = visualizer.to_ascii()

        assert "t1" in ascii_art

    def test_to_simple_ascii(self):
        """Test simplified ASCII art."""
        petri_net = AdaptivePetriNet("test")
        petri_net.set_objective("Test")
        petri_net.add_place("p1", tokens=1)
        visualizer = PetriNetVisualizer(petri_net)

        simple_ascii = visualizer.to_simple_ascii()

        assert isinstance(simple_ascii, str)
        assert "test" in simple_ascii

    def test_get_marking_str(self):
        """Test marking string representation."""
        petri_net = AdaptivePetriNet("test")
        petri_net.add_place("p1", tokens=2)
        petri_net.add_place("p2", tokens=3)
        visualizer = PetriNetVisualizer(petri_net)

        marking_str = visualizer.get_marking_str()

        assert "p1" in marking_str
        assert "p2" in marking_str
        assert "2" in marking_str
        assert "3" in marking_str

    def test_get_marking_str_empty(self):
        """Test marking string for empty net."""
        petri_net = AdaptivePetriNet("test")
        visualizer = PetriNetVisualizer(petri_net)

        marking_str = visualizer.get_marking_str()

        assert marking_str == "(empty)"

    def test_get_enabled_str(self):
        """Test enabled transitions string."""
        petri_net = AdaptivePetriNet("test")
        place = petri_net.add_place("p1", tokens=1)
        transition = petri_net.add_transition("t1")
        petri_net.add_arc(place, transition)
        visualizer = PetriNetVisualizer(petri_net)

        enabled_str = visualizer.get_enabled_str()

        assert "t1" in enabled_str

    def test_get_enabled_str_none(self):
        """Test enabled string when no transitions enabled."""
        petri_net = AdaptivePetriNet("test")
        # Create a transition that requires tokens but has none
        place = petri_net.add_place("p1", tokens=0)
        transition = petri_net.add_transition("t1")
        # Add input arc so transition requires tokens
        petri_net.add_arc(place, transition)
        visualizer = PetriNetVisualizer(petri_net)

        enabled_str = visualizer.get_enabled_str()

        assert "(none)" in enabled_str or enabled_str == ""

    def test_create_flow_diagram_no_transitions(self):
        """Test flow diagram with no transitions."""
        petri_net = AdaptivePetriNet("test")
        visualizer = PetriNetVisualizer(petri_net)

        flow = visualizer._create_flow_diagram()

        assert len(flow) > 0

    def test_create_flow_diagram_with_transitions(self):
        """Test flow diagram with transitions."""
        petri_net = AdaptivePetriNet("test")
        petri_net.set_objective("Test")
        petri_net.add_transition("t1")
        visualizer = PetriNetVisualizer(petri_net)

        flow = visualizer._create_flow_diagram()

        assert isinstance(flow, list)


class TestPrintPetriNet:
    """Tests for print_petri_net convenience function."""

    @patch('agentx.model.session.petri_net_visualizer.print')
    def test_print_petri_net_simple(self, mock_print):
        """Test printing Petri net (simple format)."""
        petri_net = AdaptivePetriNet("test")
        print_petri_net(petri_net, simple=True)

        mock_print.assert_called()

    @patch('agentx.model.session.petri_net_visualizer.print')
    def test_print_petri_net_detailed(self, mock_print):
        """Test printing Petri net (detailed format)."""
        petri_net = AdaptivePetriNet("test")
        print_petri_net(petri_net, simple=False)

        mock_print.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
