"""
Petri Net Visualizer for AgentX.

Provides ASCII art visualization of Petri Nets for debugging and display purposes.
"""

from typing import List, Dict
from agentx.model.session.adaptive_petri_net import AdaptivePetriNet, Place, Transition


class PetriNetVisualizer:
    """
    Creates ASCII art visualizations of Petri Nets.
    
    Usage:
        visualizer = PetriNetVisualizer(petri_net)
        print(visualizer.to_ascii())
    """
    
    def __init__(self, petri_net: AdaptivePetriNet):
        """
        Initialize the visualizer.
        
        Args:
            petri_net: The Petri Net to visualize
        """
        self.petri_net = petri_net
    
    def to_ascii(self) -> str:
        """
        Generate ASCII art representation of the Petri Net.
        
        Returns:
            ASCII art string
        """
        lines = []
        
        # Header
        lines.append("╔══════════════════════════════════════════════════════════════╗")
        lines.append(f"║  Petri Net: {self.petri_net.name:<49} ║")
        lines.append("╠══════════════════════════════════════════════════════════════╣")
        
        # Objective
        if self.petri_net.objective:
            obj_truncated = self.petri_net.objective[:50]
            lines.append(f"║  Objective: {obj_truncated:<49} ║")
        lines.append("╠══════════════════════════════════════════════════════════════╣")
        
        # Places (States)
        lines.append("║  PLACES (States):                                              ║")
        for place_name, place in self.petri_net.places.items():
            token_marker = "●" if place.tokens > 0 else "○"
            token_count = place.tokens
            place_line = f"║    {token_marker} {place_name:<50} "
            if token_count > 0:
                place_line += f"({token_count} tokens)"
            else:
                place_line += "(empty)"
            place_line = place_line[:63].ljust(63) + " ║"
            lines.append(place_line)
        
        lines.append("╠══════════════════════════════════════════════════════════════╣")
        
        # Transitions
        lines.append("║  TRANSITIONS (Actions):                                        ║")
        for trans_name, transition in self.petri_net.transitions.items():
            enabled = "✓" if transition.is_enabled() else " "
            inputs = ", ".join([p.name for p in transition.inputs.keys()]) or "(none)"
            outputs = ", ".join([p.name for p in transition.outputs.keys()]) or "(none)"
            
            trans_line = f"║   [{enabled}] {trans_name:<48} ║"
            lines.append(trans_line)
            
            if transition.inputs or transition.outputs:
                detail_line = f"║       In: {inputs[:48]:<48} ║"
                lines.append(detail_line)
                detail_line = f"║       Out: {outputs[:48]:<48} ║"
                lines.append(detail_line)
        
        lines.append("╠══════════════════════════════════════════════════════════════╣")
        
        # Workflow diagram (simplified)
        lines.append("║  WORKFLOW DIAGRAM:                                             ║")
        lines.append("║                                                                ║")
        
        # Create simple flow diagram
        flow_lines = self._create_flow_diagram()
        for flow_line in flow_lines:
            lines.append(f"║  {flow_line:<61} ║")
        
        lines.append("║                                                                ║")
        lines.append("╚══════════════════════════════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    def _create_flow_diagram(self) -> List[str]:
        """
        Create a simple flow diagram of the Petri Net.
        
        Returns:
            List of strings representing the flow
        """
        if not self.petri_net.transitions:
            return ["(no transitions)"]
        
        # Try to create a linear flow if possible
        flow = []
        
        # Find starting places (places with tokens)
        start_places = [name for name, place in self.petri_net.places.items() if place.tokens > 0]
        
        if not start_places:
            return ["(no starting place)"]
        
        # Build a simple chain
        visited = set()
        current_places = start_places
        
        # Limit depth to prevent infinite loops
        depth = 0
        max_depth = 10
        
        while current_places and depth < max_depth:
            depth += 1
            
            # Find enabled transitions from current places
            enabled_transitions = []
            for trans_name, transition in self.petri_net.transitions.items():
                if trans_name not in visited:
                    if transition.is_enabled():
                        enabled_transitions.append(trans_name)
            
            if not enabled_transitions:
                break
            
            # Add to flow
            for trans_name in enabled_transitions[:3]:  # Limit width
                flow.append(f"  ──[{trans_name[:15]}]──>  ")
                visited.add(trans_name)
            
            # Get next places
            next_places = []
            for trans_name in enabled_transitions[:3]:
                transition = self.petri_net.transitions.get(trans_name)
                if transition:
                    for place in transition.outputs.keys():
                        if place not in next_places:
                            next_places.append(place)
            
            current_places = next_places
        
        if not flow:
            flow = ["(no enabled transitions)"]
        
        return flow[:10]  # Limit lines
    
    def to_simple_ascii(self) -> str:
        """
        Generate simplified ASCII representation.
        
        Returns:
            Simplified ASCII art string
        """
        lines = []
        
        # Simple place -> transition -> place flow
        lines.append(f"Petri Net: {self.petri_net.name}")
        lines.append(f"Objective: {self.petri_net.objective or '(none)'}")
        lines.append("")
        
        # Show places with tokens
        lines.append("Active Places:")
        for place_name, place in self.petri_net.places.items():
            if place.tokens > 0:
                lines.append(f"  ● {place_name} ({place.tokens})")
        
        # Show enabled transitions
        lines.append("")
        lines.append("Enabled Transitions:")
        for trans_name, transition in self.petri_net.transitions.items():
            if transition.is_enabled():
                inputs = ", ".join([p.name for p in transition.inputs.keys()])
                outputs = ", ".join([p.name for p in transition.outputs.keys()])
                lines.append(f"  [{trans_name}] {inputs} --> {outputs}")
        
        return "\n".join(lines)
    
    def get_marking_str(self) -> str:
        """
        Get string representation of current marking.
        
        Returns:
            String showing token distribution
        """
        parts = []
        for place_name, place in self.petri_net.places.items():
            if place.tokens > 0:
                parts.append(f"{place_name}:{place.tokens}")
        
        if not parts:
            return "(empty)"
        
        return ", ".join(parts)
    
    def get_enabled_str(self) -> str:
        """
        Get string representation of enabled transitions.
        
        Returns:
            Comma-separated list of enabled transitions
        """
        enabled = [t.name for t in self.petri_net.enabled_transitions()]
        return ", ".join(enabled) if enabled else "(none)"


def print_petri_net(petri_net: AdaptivePetriNet, simple: bool = False):
    """
    Convenience function to print Petri Net visualization.
    
    Args:
        petri_net: The Petri Net to visualize
        simple: Use simplified format
    """
    visualizer = PetriNetVisualizer(petri_net)
    if simple:
        print(visualizer.to_simple_ascii())
    else:
        print(visualizer.to_ascii())
