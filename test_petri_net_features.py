#!/usr/bin/env python3
"""
Test script for Petri Net session state management features.

This script tests:
1. Workflow templates
2. LLM-based objective extraction
3. Dynamic Petri Net generation
4. Session state management
5. Petri Net visualization
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from agentx.model.session.workflow_templates import get_workflow_for_task, get_all_templates
from agentx.model.session.objective_extractor_llm import extract_objective_llm, TaskType
from agentx.model.session.petri_net_generator import create_session_from_prompt
from agentx.model.session.petri_net_visualizer import PetriNetVisualizer


def test_workflow_templates():
    """Test workflow template retrieval."""
    print("=" * 70)
    print("TEST 1: Workflow Templates")
    print("=" * 70)
    
    templates = get_all_templates()
    print(f"Available templates: {len(templates)}")
    for name in templates.keys():
        print(f"  - {name}")
    print()
    
    # Test specific template retrieval
    test_cases = ["debug", "analysis", "implementation", "documentation"]
    for task_type in test_cases:
        workflow = get_workflow_for_task(task_type)
        print(f"✓ {task_type}: {workflow['name']}")
        print(f"  Places: {len(workflow['places'])}")
        print(f"  Transitions: {len(workflow['transitions'])}")
    print()


def test_objective_extraction():
    """Test LLM-based objective extraction."""
    print("=" * 70)
    print("TEST 2: LLM Objective Extraction")
    print("=" * 70)
    
    test_prompts = [
        "I want to debug the login issue",
        "Analyze the project structure",
        "Add a new feature to upload files",
        "Document the API endpoints",
        "Refactor the authentication module",
    ]
    
    for prompt in test_prompts:
        print(f"Prompt: {prompt}")
        try:
            objective, task_type = extract_objective_llm(prompt)
            print(f"  Objective: {objective}")
            print(f"  Task Type: {task_type.value}")
        except Exception as e:
            print(f"  Error: {e}")
        print()


def test_petri_net_generation():
    """Test dynamic Petri Net generation."""
    print("=" * 70)
    print("TEST 3: Dynamic Petri Net Generation")
    print("=" * 70)
    
    test_prompts = [
        "Debug the API 500 error",
        "Analyze the codebase structure",
        "Implement file upload feature",
    ]
    
    for prompt in test_prompts:
        print(f"Prompt: {prompt}")
        try:
            manager = create_session_from_prompt(prompt)
            state = manager.get_state()
            
            print(f"  ✓ Session created")
            print(f"  Objective: {state.objective}")
            print(f"  Task Type: {state.context.get('task_type', 'unknown')}")
            print(f"  Workflow: {state.context.get('workflow_name', 'unknown')}")
            print(f"  Status: {state.context.get('objective_status', 'pending')}")
            print(f"  Enabled: {state.context.get('enabled_transitions', [])}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        print()


def test_visualization():
    """Test Petri Net visualization."""
    print("=" * 70)
    print("TEST 4: Petri Net Visualization")
    print("=" * 70)
    
    prompt = "Debug the login authentication issue"
    print(f"Creating session from: {prompt}")
    
    try:
        manager = create_session_from_prompt(prompt)
        visualizer = PetriNetVisualizer(manager.petri_net)
        
        print("\n--- Full ASCII Art ---")
        print(visualizer.to_ascii())
        
        print("\n--- Simple View ---")
        print(visualizer.to_simple_ascii())
        
        print("\n--- Marking ---")
        print(visualizer.get_marking_str())
        
        print("\n--- Enabled Transitions ---")
        print(visualizer.get_enabled_str())
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    print()


def test_workflow_advancement():
    """Test advancing through workflow."""
    print("=" * 70)
    print("TEST 5: Workflow Advancement")
    print("=" * 70)
    
    prompt = "Debug the database connection error"
    print(f"Creating session: {prompt}")
    
    try:
        manager = create_session_from_prompt(prompt)
        
        # Get initial state
        state = manager.get_state()
        print(f"\nInitial State:")
        print(f"  Status: {state.context.get('objective_status')}")
        print(f"  Enabled: {state.context.get('enabled_transitions', [])}")
        
        # Advance through workflow
        step = 1
        while True:
            enabled = state.context.get('enabled_transitions', [])
            if not enabled:
                print(f"\n✓ Workflow complete or stuck")
                break
            
            # Fire first enabled transition
            transition = enabled[0]
            print(f"\nStep {step}: Firing '{transition}'")
            
            success = manager.advance_objective(transition)
            if not success:
                print(f"  ✗ Failed to fire transition")
                break
            
            state = manager.get_state()
            print(f"  Status: {state.context.get('objective_status')}")
            print(f"  Next: {state.context.get('enabled_transitions', [])}")
            
            # Check if complete
            if manager.is_complete():
                print(f"\n✓ Objective completed!")
                break
            
            step += 1
            if step > 10:  # Safety limit
                print("\n⚠ Reached step limit")
                break
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("PETRI NET SESSION STATE MANAGEMENT - TEST SUITE")
    print("=" * 70 + "\n")
    
    try:
        test_workflow_templates()
        test_objective_extraction()
        test_petri_net_generation()
        test_visualization()
        test_workflow_advancement()
        
        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETED")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
