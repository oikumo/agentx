from datetime import datetime, timezone
from typing import Any, Optional
from model.session.adaptive_petri_net import AdaptivePetriNet, SessionState


class SessionStateManager:
    """
    Manages session state using an Adaptive Petri Net.
    
    The Petri net models the user's objective as tokens flowing through
    different states (pending -> in_progress -> completed).
    """
    
    def __init__(self, session_name: str = "default"):
        self.session_name = session_name
        self.petri_net = AdaptivePetriNet(name=f"{session_name}_session")
        self.created_at: str = ""
        self.updated_at: str = ""
        self._initialize()
    
    def _initialize(self):
        """Initialize the session state manager."""
        now = datetime.now(timezone.utc)
        self.created_at = now.isoformat()
        self.updated_at = now.isoformat()
    
    def set_objective(self, objective: str, initial_context: Optional[dict[str, Any]] = None):
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
    
    def update_context(self, key: str, value: Any):
        """Update context data in the session state."""
        self.petri_net.add_place(key, tokens=1)
        self._update_timestamp()
    
    def advance_objective(self, transition_name: str) -> bool:
        """
        Advance the objective state by firing a transition.
        
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
    
    def is_complete(self) -> bool:
        """Check if the session objective is complete."""
        return self.petri_net.is_complete()
    
    def reset(self):
        """Reset the session state."""
        self.petri_net.reset()
        self._update_timestamp()
    
    def _update_timestamp(self):
        """Update the session timestamp."""
        self.updated_at = datetime.now(timezone.utc).isoformat()
    
    def get_history(self) -> list[dict]:
        """Get the state history."""
        return self.petri_net.state_history.copy()
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize session state to dictionary."""
        state = self.get_state()
        return {
            "session_name": self.session_name,
            "objective": state.objective,
            "context": state.context,
            "marking": self.petri_net.marking(),
            "enabled_transitions": [t.name for t in self.petri_net.enabled_transitions()],
            "is_complete": self.is_complete(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "history_length": len(self.get_history())
        }
    
    def __repr__(self):
        state = self.get_state()
        return (
            f"SessionStateManager(session={self.session_name!r}, "
            f"objective={state.objective!r}, "
            f"complete={self.is_complete()})"
        )


class SessionStateBuilder:
    """
    Builder for creating session states with Adaptive Petri Net.
    
    Usage:
        builder = SessionStateBuilder("user_session")
        builder.set_objective("Analyze project structure")
        builder.add_transition("start_analysis", ["objective_pending"], ["objective_in_progress"])
        builder.add_transition("complete_analysis", ["objective_in_progress"], ["objective_completed"])
        state_manager = builder.build()
    """
    
    def __init__(self, session_name: str = "default"):
        self.session_name = session_name
        self.petri_net = AdaptivePetriNet(name=f"{session_name}_session")
        self.transitions: list[tuple[str, list[str], list[str]]] = []
    
    def set_objective(self, objective: str):
        """Set the session objective."""
        self.petri_net.set_objective(objective)
        return self
    
    def add_transition(self, name: str, inputs: list[str], outputs: list[str]):
        """Add a transition to the Petri net."""
        self.transitions.append((name, inputs, outputs))
        return self
    
    def build(self) -> SessionStateManager:
        """Build the session state manager."""
        # Create standard objective places
        self.petri_net.add_place("objective_pending", tokens=1)
        self.petri_net.add_place("objective_in_progress", tokens=0)
        self.petri_net.add_place("objective_completed", tokens=0)
        
        # Add transitions
        for name, inputs, outputs in self.transitions:
            transition = self.petri_net.add_transition(name)
            
            # Connect inputs
            for input_place in inputs:
                if input_place in self.petri_net.places:
                    self.petri_net.add_arc(
                        self.petri_net.places[input_place],
                        transition
                    )
            
            # Connect outputs
            for output_place in outputs:
                if output_place in self.petri_net.places:
                    self.petri_net.add_arc(
                        transition,
                        self.petri_net.add_place(output_place, tokens=0)
                    )
        
        manager = SessionStateManager(self.session_name)
        manager.petri_net = self.petri_net
        return manager
