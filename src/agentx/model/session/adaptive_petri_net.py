from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, TYPE_CHECKING
from enum import Enum


@dataclass
class SessionState:
    """Represents the current state of a session."""
    objective: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


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
        self.places: dict[str, Place] = {}
        self.transitions: dict[str, Transition] = {}
        self.objective: Optional[str] = None
        self.state_history: list[dict] = []
        
    def add_place(self, name: str, tokens: int = 0) -> Place:
        """Add a new place to the net."""
        if name not in self.places:
            p = Place(name, tokens)
            self.places[name] = p
        return self.places[name]
    
    def add_transition(self, name: str) -> Transition:
        """Add a new transition to the net."""
        if name not in self.transitions:
            t = Transition(name)
            self.transitions[name] = t
        return self.transitions[name]
    
    def add_arc(self, src, dst, weight: int = 1):
        """Connect place -> transition or transition -> place."""
        if isinstance(src, Place) and isinstance(dst, Transition):
            dst.add_input(src, weight)
        elif isinstance(src, Transition) and isinstance(dst, Place):
            src.add_output(dst, weight)
        else:
            raise ValueError("Arc must connect Place->Transition or Transition->Place")
    
    def set_objective(self, objective: str, initial_tokens: dict[str, int] = None):
        """
        Set the user objective and initialize the Petri net.
        
        The objective becomes the driving force for token flow.
        Initial tokens can be provided to seed specific places.
        """
        self.objective = objective
        
        # Create standard places for objective tracking
        self.add_place("objective_pending", tokens=1)
        self.add_place("objective_in_progress", tokens=0)
        self.add_place("objective_completed", tokens=0)
        
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
    
    def marking(self) -> dict[str, int]:
        """Get current token distribution."""
        return {name: p.tokens for name, p in self.places.items()}
    
    def enabled_transitions(self) -> list[Transition]:
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
        if hasattr(self, '_metadata') and self._metadata:
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
        self.inputs: dict[Place, int] = {}
        self.outputs: dict[Place, int] = {}
    
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


@dataclass
class AdaptivePetriNetConfig:
    """Configuration for adaptive Petri net behavior."""
    auto_save: bool = True
    max_history: int = 100
    enable_adaptation: bool = True
