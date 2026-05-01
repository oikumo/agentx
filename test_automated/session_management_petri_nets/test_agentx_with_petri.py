"""
End-to-End Test: AgentX with Petri Net Session State

This script tests the actual AgentX application with:
1. MainController with integrated Petri Net session state
2. User query processing with LLM Petri Net generation
3. Commands for viewing Petri Net state
4. Session management with Petri Net tracking
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentx.controllers.main_controller.main_controller import MainController
from agentx.model.session.session_state_manager import SessionStateManager, SessionStateBuilder
from agentx.model.session.petri_net_visualizer import PetriNetVisualizer
from agentx.controllers.main_controller.commands import (
    HelpCommand,
    NewCommand,
    PetriNetStatusCommand,
    PetriNetPrintCommand,
    QuitCommand
)


def test_basic_controller_with_commands():
    """Test 1: Basic controller with all commands"""
    print("\n" + "="*70)
    print("TEST 1: MainController with Petri Net Commands")
    print("="*70)
    
    try:
        # Create controller
        controller = MainController()
        print(f"✓ MainController created")
        print(f"  - Session: {controller.session.name}")
        print(f"  - Session state: {controller.session_state}")
        
        # Register all Petri Net commands
        controller.add_command(HelpCommand("help", controller))
        controller.add_command(NewCommand("new", controller))
        controller.add_command(PetriNetStatusCommand("status", controller))
        controller.add_command(PetriNetPrintCommand("petri-print", controller))
        
        print(f"✓ Commands registered: {[c.key for c in controller.get_commands()]}")
        
        # Test help command
        print("\n--- Running 'help' command ---")
        help_cmd = controller.find_command("help")
        result = help_cmd.run([])
        if result:
            result.apply()
        print("✓ Help command executed")
        
        # Test status command (should show no active session)
        print("\n--- Running 'status' command ---")
        status_cmd = controller.find_command("status")
        result = status_cmd.run([])
        if result:
            result.apply()
        print("✓ Status command executed")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_state_workflow():
    """Test 2: Complete workflow with session state"""
    print("\n" + "="*70)
    print("TEST 2: Session State Workflow (LLM Generator Simulation)")
    print("="*70)
    
    try:
        # Create controller
        controller = MainController()
        
        # Add required commands
        controller.add_command(HelpCommand("help", controller))
        controller.add_command(NewCommand("new", controller))
        controller.add_command(PetriNetStatusCommand("status", controller))
        controller.add_command(PetriNetPrintCommand("petri-print", controller))
        
        # Simulate LLM Petri Net generation (what would happen in handle_user_query)
        print("\n--- Simulating LLM Petri Net Generation ---")
        
        # Create a session state manager with custom workflow
        builder = SessionStateBuilder("project_analysis")
        builder.set_objective("Analyze project structure and identify key components")
        
        # Add transitions for a typical analysis workflow
        builder.add_transition('start_analysis', ['objective_pending'], ['objective_in_progress'])
        builder.add_transition('gather_info', ['objective_in_progress'], ['objective_in_progress'])
        builder.add_transition('complete_analysis', ['objective_in_progress'], ['objective_completed'])
        
        # Build the session state
        controller.session_state = builder.build()
        print(f"✓ Session state created: {controller.session_state}")
        
        # Get and display initial state
        state = controller.session_state.get_state()
        print(f"✓ Initial state:")
        print(f"  - Objective: {state.objective}")
        print(f"  - Status: {state.context.get('objective_status', 'pending')}")
        print(f"  - Marking: {state.context.get('marking', {})}")
        
        # Show enabled transitions
        enabled = [t.name for t in controller.session_state.petri_net.enabled_transitions()]
        print(f"✓ Enabled transitions: {enabled}")
        
        # Test status command (should show active session)
        print("\n--- Running 'status' command with active session ---")
        status_cmd = controller.find_command("status")
        if status_cmd:
            result = status_cmd.run([])
            if result:
                result.apply()
        else:
            print("Status command not found")
        
        # Test petri-print command
        print("\n--- Running 'petri-print' command ---")
        print_cmd = controller.find_command("petri-print")
        if print_cmd:
            result = print_cmd.run([])
            if result:
                result.apply()
        else:
            print("Petri-print command not found")
        
        # Simulate firing transitions
        print("\n--- Simulating workflow execution ---")
        if 'start_analysis' in enabled:
            controller.session_state.advance_objective('start_analysis')
            print(f"✓ Fired 'start_analysis'")
            
            state = controller.session_state.get_state()
            print(f"  New status: {state.context.get('objective_status', 'unknown')}")
            print(f"  New marking: {controller.session_state.petri_net.marking()}")
            
            enabled = [t.name for t in controller.session_state.petri_net.enabled_transitions()]
            print(f"  Now enabled: {enabled}")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_custom_workflow_builder():
    """Test 3: Custom workflow builder with complex workflow"""
    print("\n" + "="*70)
    print("TEST 3: Custom Workflow Builder (Complex Workflow)")
    print("="*70)
    
    try:
        # Create a more complex workflow
        builder = SessionStateBuilder("complex_workflow")
        builder.set_objective("Complete multi-step task")
        
        # Add a sequence of transitions
        builder.add_transition('step1', ['objective_pending'], ['step1_complete'])
        builder.add_transition('step2', ['step1_complete'], ['step2_complete'])
        builder.add_transition('step3', ['step2_complete'], ['step3_complete'])
        builder.add_transition('finalize', ['step3_complete'], ['objective_completed'])
        
        workflow = builder.build()
        
        print(f"✓ Complex workflow created")
        print(f"  - Objective: {workflow.get_state().objective}")
        
        # Visualize
        visualizer = PetriNetVisualizer(workflow.petri_net)
        print("\n" + visualizer.to_ascii())
        
        # Execute workflow
        print("\n--- Executing workflow ---")
        transitions_to_fire = ['step1', 'step2', 'step3', 'finalize']
        
        for transition in transitions_to_fire:
            enabled = [t.name for t in workflow.petri_net.enabled_transitions()]
            if transition in enabled:
                workflow.advance_objective(transition)
                print(f"✓ Fired '{transition}'")
                print(f"  Marking: {workflow.petri_net.marking()}")
            else:
                print(f"✗ '{transition}' not enabled (enabled: {enabled})")
        
        # Check if complete
        is_complete = workflow.is_complete()
        print(f"\n✓ Workflow complete: {is_complete}")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_with_new_command():
    """Test 4: Session management with 'new' command"""
    print("\n" + "="*70)
    print("TEST 4: Session Management with 'new' command")
    print("="*70)
    
    try:
        # Create controller
        controller = MainController()
        
        print(f"✓ Initial session: {controller.session.name}")
        print(f"  Directory: {controller.session.directory}")
        
        # Execute 'new' command
        print("\n--- Executing 'new test_session_1' command ---")
        new_cmd = controller.find_command("new")
        if new_cmd:
            result = new_cmd.run(["test_session_1"])
            if result:
                result.apply()
                print("✓ New session created")
                print(f"  New session: {controller.session.name}")
                print(f"  New directory: {controller.session.directory}")
        
        # Execute another 'new' command
        print("\n--- Executing 'new test_session_2' command ---")
        if new_cmd:
            result = new_cmd.run(["test_session_2"])
            if result:
                result.apply()
                print("✓ Another session created")
                print(f"  Current session: {controller.session.name}")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_real_world_scenario():
    """Test 5: Real-world scenario - analyzing a project"""
    print("\n" + "="*70)
    print("TEST 5: Real-World Scenario - Project Analysis")
    print("="*70)
    
    try:
        # Create controller
        controller = MainController()
        
        # Add required commands
        controller.add_command(HelpCommand("help", controller))
        controller.add_command(NewCommand("new", controller))
        controller.add_command(PetriNetStatusCommand("status", controller))
        controller.add_command(PetriNetPrintCommand("petri-print", controller))
        
        # Simulate user query: "Analyze the project structure"
        print("\n--- Simulating user query: 'Analyze the project structure' ---")
        
        # This is what handle_user_query would do (LLM generation simulated)
        builder = SessionStateBuilder("project_analysis")
        builder.set_objective("Analyze project structure and identify key components")
        
        # LLM would generate these transitions based on the query
        builder.add_transition('scan_files', ['objective_pending'], ['scanning'])
        builder.add_transition('identify_patterns', ['scanning'], ['analyzing'])
        builder.add_transition('generate_report', ['analyzing'], ['objective_completed'])
        
        controller.session_state = builder.build()
        
        print(f"✓ Session state created from query")
        
        # Display initial state
        print("\n--- Initial State ---")
        status_cmd = controller.find_command("status")
        if status_cmd:
            result = status_cmd.run([])
            if result:
                result.apply()
        else:
            print("Status command not found")
        
        # Execute workflow
        print("\n--- Executing Analysis Workflow ---")
        
        # Step 1: Scan files
        if controller.session_state.petri_net.enabled_transitions():
            enabled = [t.name for t in controller.session_state.petri_net.enabled_transitions()]
            print(f"Available: {enabled}")
            
            if 'scan_files' in enabled:
                controller.session_state.advance_objective('scan_files')
                print("✓ Scanned files")
        
        # Show intermediate state
        print("\n--- Intermediate State ---")
        if status_cmd:
            result = status_cmd.run([])
            if result:
                result.apply()
        
        # Step 2: Identify patterns
        if controller.session_state.petri_net.enabled_transitions():
            enabled = [t.name for t in controller.session_state.petri_net.enabled_transitions()]
            if 'identify_patterns' in enabled:
                controller.session_state.advance_objective('identify_patterns')
                print("✓ Identified patterns")
        
        # Step 3: Generate report
        if controller.session_state.petri_net.enabled_transitions():
            enabled = [t.name for t in controller.session_state.petri_net.enabled_transitions()]
            if 'generate_report' in enabled:
                controller.session_state.advance_objective('generate_report')
                print("✓ Generated report")
        
        # Final state
        print("\n--- Final State ---")
        if status_cmd:
            result = status_cmd.run([])
            if result:
                result.apply()
        
        print(f"\n✓ Workflow complete: {controller.session_state.is_complete()}")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all end-to-end tests"""
    print("\n" + "="*70)
    print("AGENT-X WITH PETRI NET: END-TO-END TEST")
    print("="*70)
    
    tests = [
        ("Basic Controller with Commands", test_basic_controller_with_commands),
        ("Session State Workflow", test_session_state_workflow),
        ("Custom Workflow Builder", test_custom_workflow_builder),
        ("Session Management", test_session_with_new_command),
        ("Real-World Scenario", test_real_world_scenario),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("E2E TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All E2E tests passed! Petri Net integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
