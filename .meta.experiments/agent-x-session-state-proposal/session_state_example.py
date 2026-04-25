"""
Example: Using Adaptive Petri Net Session State with MainController

This example demonstrates how to integrate the AdaptivePetriNet-based
session state management into the MainController.
"""

from model.session import SessionStateManager, SessionStateBuilder


def example_basic_usage():
    """Basic usage of SessionStateManager."""
    print("\n=== Example 1: Basic Usage ===")
    
    manager = SessionStateManager("user_session")
    manager.set_objective("Analyze project structure and identify key components")
    
    state = manager.get_state()
    print(f"Objective: {state.objective}")
    print(f"Status: {state.context['objective_status']}")
    print(f"Marking: {state.context['marking']}")
    
    return manager


def example_builder_pattern():
    """Using the builder pattern for custom workflows."""
    print("\n=== Example 2: Builder Pattern ===")
    
    builder = SessionStateBuilder("analysis_session")
    builder.set_objective("Complete project analysis")
    
    builder.add_transition(
        'start_analysis',
        ['objective_pending'],
        ['objective_in_progress']
    )
    builder.add_transition(
        'complete_analysis',
        ['objective_in_progress'],
        ['objective_completed']
    )
    
    manager = builder.build()
    state = manager.get_state()
    
    print(f"Objective: {state.objective}")
    print(f"Enabled transitions: {[t.name for t in manager.petri_net.enabled_transitions()]}")
    
    manager.advance_objective('start_analysis')
    
    state = manager.get_state()
    print(f"After firing 'start_analysis':")
    print(f"  Marking: {state.context['marking']}")
    print(f"  Status: {state.context['objective_status']}")
    
    return manager


def example_integration_with_maincontroller():
    """Example of integrating with MainController."""
    print("\n=== Example 3: MainController Integration ===")
    
    manager = SessionStateManager("main_controller_session")
    manager.set_objective("Help user with their task")
    
    print(f"Session state manager created: {manager}")
    print(f"Initial state: {manager.get_state()}")
    
    manager.update_context("user_query", "Analyze the project")
    manager.update_context("timestamp", "2026-04-25")
    
    print(f"Context updated: {manager.get_state().context}")
    
    return manager


def example_state_serialization():
    """Example of serializing session state."""
    print("\n=== Example 4: State Serialization ===")
    
    manager = SessionStateManager("serialize_test")
    manager.set_objective("Test serialization")
    
    state_dict = manager.to_dict()
    
    print("Serialized state:")
    for key, value in state_dict.items():
        if key != 'history_length':
            print(f"  {key}: {value}")
    
    return state_dict


def example_petri_net_flow():
    """Demonstrate Petri net token flow."""
    print("\n=== Example 5: Petri Net Token Flow ===")
    
    builder = SessionStateBuilder("workflow_demo")
    builder.set_objective("Complete workflow")
    
    builder.add_transition('begin', ['objective_pending'], ['objective_in_progress'])
    builder.add_transition('finish', ['objective_in_progress'], ['objective_completed'])
    
    manager = builder.build()
    
    print("Initial state:")
    print(f"  Marking: {manager.petri_net.marking()}")
    print(f"  Enabled: {[t.name for t in manager.petri_net.enabled_transitions()]}")
    
    print("\nFiring 'begin' transition...")
    manager.advance_objective('begin')
    print(f"  Marking: {manager.petri_net.marking()}")
    print(f"  Enabled: {[t.name for t in manager.petri_net.enabled_transitions()]}")
    
    print("\nFiring 'finish' transition...")
    manager.advance_objective('finish')
    print(f"  Marking: {manager.petri_net.marking()}")
    print(f"  Is complete: {manager.is_complete()}")
    
    return manager


if __name__ == "__main__":
    print("=" * 60)
    print("Adaptive Petri Net Session State Examples")
    print("=" * 60)
    
    example_basic_usage()
    example_builder_pattern()
    example_integration_with_maincontroller()
    example_state_serialization()
    example_petri_net_flow()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
