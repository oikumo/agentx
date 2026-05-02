"""
Session Petri Net - Isolated Module

This module provides a single, clean interface for managing session state
using Adaptive Petri Nets. It encapsulates all Petri net functionality
for session management, objective tracking, and state transitions.

Usage:
    from agentx.model.session.session_petri_net import SessionPetriNet

    # Create a new session Petri net
    petri = SessionPetriNet("my_session")
    
    # Set objective and initialize
    petri.set_objective("Analyze project structure")
    
    # Fire transitions
    petri.fire("start_analysis")
    
    # Get current state
    state = petri.get_state()
    
    # Check if complete
    if petri.is_complete():
        print("Objective completed!")
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List
from datetime import datetime, timezone
from enum import Enum


# ============================================================================
# Core Data Classes
# ============================================================================

@dataclass
class SessionState:
    """Represents the current state of a session."""
    objective: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


@dataclass
class PetriNetState:
    """Snapshot of Petri net state."""
    marking: Dict[str, int]
    enabled_transitions: List[str]
    objective_status: str
    objective: str
    history_length: int


# ============================================================================
# Petri Net Core Components
# ============================================================================

class Place:
    """A place in the Petri net that holds tokens."""
    
    def __init__(self, name: str, tokens: int = 0):
        if tokens < 0:
            raise ValueError("Token count cannot be negative.")
        self.name = name
        self.tokens = tokens
    
    def __repr__(self):
        return f"Place({self.name!r}, tokens={self.tokens})"


class Transition:
    """A transition that can fire when enabled."""
    
    def __init__(self, name: str):
        self.name = name
        self.inputs: Dict[Place, int] = {}
        self.outputs: Dict[Place, int] = {}
    
    def add_input(self, place: Place, weight: int = 1):
        """Add an input arc from a place."""
        self.inputs[place] = weight
    
    def add_output(self, place: Place, weight: int = 1):
        """Add an output arc to a place."""
        self.outputs[place] = weight
    
    def is_enabled(self) -> bool:
        """Check if transition can fire."""
        return all(place.tokens >= w for place, w in self.inputs.items())
    
    def fire(self) -> bool:
        """Fire the transition if enabled."""
        if not self.is_enabled():
            return False
        
        # Consume from inputs
        for place, w in self.inputs.items():
            place.tokens -= w
        
        # Produce to outputs
        for place, w in self.outputs.items():
            place.tokens += w
        
        return True
    
    def __repr__(self):
        return f"Transition({self.name!r})"


# ============================================================================
# Adaptive Petri Net
# ============================================================================

class AdaptivePetriNet:
    """
    Adaptive Petri Net for modeling user objectives and session state.
    
    Extends basic Petri net with:
    - Dynamic place/transition creation
    - Objective-driven token flow
    - State tracking for session management
    """
    
    def __init__(self, name: str = "SessionPetriNet"):
        self.name = name
        self.places: Dict[str, Place] = {}
        self.transitions: Dict[str, Transition] = {}
        self.objective: Optional[str] = None
        self.state_history: List[Dict] = []
        self._metadata: Dict[str, Any] = {}
    
    def add_place(self, name: str, tokens: int = 0) -> Place:
        """Add a new place to the net."""
        if name not in self.places:
            p = Place(name, tokens)
            self.places[name] = p
            return self.places[name]
        return self.places[name]
    
    def add_transition(self, name: str) -> Transition:
        """Add a new transition to the net."""
        if name not in self.transitions:
            t = Transition(name)
            self.transitions[name] = t
            return self.transitions[name]
        return self.transitions[name]
    
    def add_arc(self, src, dst, weight: int = 1):
        """Connect place -> transition or transition -> place."""
        if isinstance(src, Place) and isinstance(dst, Transition):
            dst.add_input(src, weight)
        elif isinstance(src, Transition) and isinstance(dst, Place):
            src.add_output(dst, weight)
        else:
            raise ValueError("Arc must connect Place->Transition or Transition->Place")
    
    def set_objective(self, objective: str, initial_tokens: Dict[str, int] = None):
        """
        Set the user objective and initialize the Petri net.
        
        The objective becomes the driving force for token flow.
        Initial tokens can be provided to seed specific places.
        
        Automatically creates standard transitions:
        - "start": moves token from pending to in_progress
        - "finish": moves token from in_progress to completed
        """
        self.objective = objective
        
        # Create standard places for objective tracking
        self.add_place("objective_pending", tokens=1)
        self.add_place("objective_in_progress", tokens=0)
        self.add_place("objective_completed", tokens=0)
        
        # Create standard transitions
        start_transition = self.add_transition("start")
        finish_transition = self.add_transition("finish")
        
        # Connect arcs for "start" transition (pending -> in_progress)
        pending_place = self.places["objective_pending"]
        in_progress_place = self.places["objective_in_progress"]
        self.add_arc(pending_place, start_transition)
        self.add_arc(start_transition, in_progress_place)
        
        # Connect arcs for "finish" transition (in_progress -> completed)
        completed_place = self.places["objective_completed"]
        self.add_arc(in_progress_place, finish_transition)
        self.add_arc(finish_transition, completed_place)
        
        # Add user-provided initial tokens
        if initial_tokens:
            for place_name, tokens in initial_tokens.items():
                if place_name in self.places:
                    self.places[place_name].tokens = tokens
        
        self._save_state()
    
    def fire_transition(self, transition_name: str) -> bool:
        """Fire a transition if enabled and save state."""
        if transition_name not in self.transitions:
            return False
        
        transition = self.transitions[transition_name]
        if transition.fire():
            self._save_state()
            return True
        return False
    
    def _save_state(self):
        """Save current marking to history."""
        self.state_history.append({
            "marking": self.marking(),
            "enabled": [t.name for t in self.enabled_transitions()],
            "objective": self.objective
        })
    
    def marking(self) -> Dict[str, int]:
        """Get current token distribution."""
        return {name: p.tokens for name, p in self.places.items()}
    
    def enabled_transitions(self) -> List[Transition]:
        """Get list of enabled transitions."""
        return [t for t in self.transitions.values() if t.is_enabled()]
    
    def get_state(self) -> SessionState:
        """Extract current session state from Petri net marking."""
        marking = self.marking()
        
        # Determine objective status from marking
        objective_status = "pending"
        if marking.get("objective_completed", 0) > 0:
            objective_status = "completed"
        elif marking.get("objective_in_progress", 0) > 0:
            objective_status = "in_progress"
        
        # Build context with marking and status
        context = {
            "marking": marking,
            "objective_status": objective_status,
            "enabled_transitions": [t.name for t in self.enabled_transitions()]
        }
        
        # Include metadata if available
        context.update(self._metadata)
        
        return SessionState(
            objective=self.objective or "",
            context=context
        )
    
    def is_complete(self) -> bool:
        """Check if objective is complete."""
        return self.places.get("objective_completed", Place("temp")).tokens > 0
    
    def reset(self):
        """Reset the net to initial state."""
        for place in self.places.values():
            place.tokens = 0
        self.state_history.clear()
        self.objective = None
        self._metadata.clear()
    
    def get_snapshot(self) -> PetriNetState:
        """Get a snapshot of current state."""
        state = self.get_state()
        return PetriNetState(
            marking=self.marking(),
            enabled_transitions=[t.name for t in self.enabled_transitions()],
            objective_status=state.context.get("objective_status", "pending"),
            objective=self.objective or "",
            history_length=len(self.state_history)
        )


# ============================================================================
# Session Petri Net - Main Interface
# ============================================================================

class SessionPetriNet:
    """
    Main interface for Session Petri Net functionality.
    
    This is the single entry point for all session state management
    using Petri nets. It provides a clean, high-level API that
    encapsulates the underlying AdaptivePetriNet implementation.
    
    Usage:
        # Create and initialize
        petri = SessionPetriNet("my_session")
        petri.set_objective("Analyze project")
        
        # Fire transitions
        petri.fire("start")
        
        # Get state
        state = petri.get_state()
        print(f"Status: {state.context['objective_status']}")
        
        # Check completion
        if petri.is_complete():
            print("Done!")
    """
    
    def __init__(self, session_name: str = "default"):
        """
        Initialize Session Petri Net.
        
        Args:
            session_name: Name identifier for this session
        """
        self.session_name = session_name
        self.petri_net = AdaptivePetriNet(name=f"{session_name}_session")
        self.created_at: str = ""
        self.updated_at: str = ""
        self._initialize()
    
    def _initialize(self):
        """Initialize timestamps and state."""
        now = datetime.now(timezone.utc)
        self.created_at = now.isoformat()
        self.updated_at = now.isoformat()
    
    # ------------------------------------------------------------------------
    # Core Operations
    # ------------------------------------------------------------------------
    
    def set_objective(self, objective: str, initial_context: Optional[Dict[str, Any]] = None):
        """
        Set the user's objective for this session.
        
        This creates the initial Petri net structure with:
        - objective_pending place (1 token)
        - objective_in_progress place (0 tokens)
        - objective_completed place (0 tokens)
        
        Args:
            objective: The user's objective statement
            initial_context: Optional context data to store
        """
        self.petri_net.set_objective(objective, initial_tokens={})
        self._update_timestamp()
        
        # Store initial context if provided
        if initial_context:
            self.petri_net.add_place("context_tokens", tokens=1)
    
    def fire(self, transition_name: str) -> bool:
        """
        Fire a transition to advance session state.
        
        Args:
            transition_name: Name of the transition to fire
            
        Returns:
            True if transition fired successfully, False otherwise
        """
        success = self.petri_net.fire_transition(transition_name)
        if success:
            self._update_timestamp()
        return success
    
    def get_state(self) -> SessionState:
        """Get the current session state."""
        return self.petri_net.get_state()
    
    def get_snapshot(self) -> PetriNetState:
        """Get a snapshot of current Petri net state."""
        return self.petri_net.get_snapshot()
    
    def is_complete(self) -> bool:
        """Check if the session objective is complete."""
        return self.petri_net.is_complete()
    
    def reset(self):
        """Reset the session state to initial."""
        self.petri_net.reset()
        self._update_timestamp()
    
    # ------------------------------------------------------------------------
    # Advanced Operations
    # ------------------------------------------------------------------------
    
    def add_place(self, name: str, tokens: int = 0):
        """Add a custom place to the Petri net."""
        self.petri_net.add_place(name, tokens)
        self._update_timestamp()
    
    def add_transition(self, name: str):
        """Add a custom transition to the Petri net."""
        self.petri_net.add_transition(name)
        self._update_timestamp()
    
    def add_arc(self, src, dst, weight: int = 1):
        """Add an arc connecting places and transitions."""
        self.petri_net.add_arc(src, dst, weight)
        self._update_timestamp()
    
    def get_marking(self) -> Dict[str, int]:
        """Get current token distribution."""
        return self.petri_net.marking()
    
    def get_enabled_transitions(self) -> List[str]:
        """Get list of enabled transition names."""
        return [t.name for t in self.petri_net.enabled_transitions()]
    
    def get_history(self) -> List[Dict]:
        """Get the state history."""
        return self.petri_net.state_history.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize session state to dictionary."""
        state = self.get_state()
        return {
            "session_name": self.session_name,
            "objective": state.objective,
            "context": state.context,
            "marking": self.get_marking(),
            "enabled_transitions": self.get_enabled_transitions(),
            "is_complete": self.is_complete(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "history_length": len(self.get_history())
        }
    
    # ------------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------------
    
    def _update_timestamp(self):
        """Update the session timestamp."""
        self.updated_at = datetime.now(timezone.utc).isoformat()
    
    def __repr__(self):
        state = self.get_state()
        return (
            f"SessionPetriNet(session={self.session_name!r}, "
            f"objective={state.objective!r}, "
            f"complete={self.is_complete()})"
        )


# ============================================================================
# Convenience Functions
# ============================================================================

def create_session_petri_net(session_name: str = "default") -> SessionPetriNet:
    """
    Create a new SessionPetriNet instance.
    
    This is a convenience function for creating session Petri nets
    with a simple function call.
    
    Args:
        session_name: Name for the session
        
    Returns:
        New SessionPetriNet instance
    """
    return SessionPetriNet(session_name)


def create_from_objective(objective: str, session_name: str = "default") -> SessionPetriNet:
    """
    Create a SessionPetriNet and set its objective in one call.
    
    This is a convenience function for the common pattern of
    creating a session and immediately setting its objective.
    
    Args:
        objective: The session objective
        session_name: Name for the session
        
    Returns:
        SessionPetriNet with objective set
    """
    petri = SessionPetriNet(session_name)
    petri.set_objective(objective)
    return petri


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Main interface
    'SessionPetriNet',
    
    # Core components (for advanced usage)
    'AdaptivePetriNet',
    'Place',
    'Transition',
    
    # Data classes
    'SessionState',
    'PetriNetState',
    
    # Convenience functions
    'create_session_petri_net',
    'create_from_objective',
]
