"""
Test script for Petri Net Session State Integration with AgentX

This script tests:
1. SessionManager integration with MainController
2. SessionStateManager with Petri Net
3. Commands integration (status, petri-print)
4. Visual representation of Petri Net
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentx.model.session.session_manager import SessionManager, get_session_manager
from agentx.model.session.session_state_manager import SessionStateManager, SessionStateBuilder
from agentx.model.session.adaptive_petri_net import AdaptivePetriNet
from agentx.model.session.petri_net_visualizer import PetriNetVisualizer
from agentx.controllers.main_controller.main_controller import MainController
from agentx.controllers.main_controller.commands import (
    NewCommand, 
    HelpCommand, 
    PetriNetStatusCommand,
    PetriNetPrintCommand
)

def test_session_manager():
    """Test 1: SessionManager basic functionality"""
    print("\n" + "="*60)
    print("TEST 1: SessionManager Basic Functionality")
    print("="*60)
    
    try:
        # Get session manager (should create default session)
        sm = get_session_manager()
        session = sm.get_current_session()
        
        print(f"✓ Session manager created: {sm}")
        print(f"✓ Current session: {session.name}")
        print(f"✓ Session directory: {session.directory}")
        print(f"✓ Has session: {sm.has_session()}")
        
        # Test database
        db = sm.get_database()
        if db:
            print(f"✓ Database connected: {db}")
        else:
            print("✗ Database not connected")
            
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_state_manager():
    """Test 2: SessionStateManager with Petri Net"""
    print("\n" + "="*60)
    print("TEST 2: SessionStateManager with Petri Net")
    print("="*60)
    
    try:
        # Create session state manager
        ssm = SessionStateManager("test_session")
        
        print(f"✓ SessionStateManager created: {ssm}")
        
        # Set an objective
        ssm.set_objective("Analyze project structure and identify key components")
        print(f"✓ Objective set")
        
        # Get state
        state = ssm.get_state()
        print(f"✓ State retrieved:")
        print(f"  - Objective: {state.objective}")
        print(f"  - Context: {state.context}")
        
        # Check marking
        marking = ssm.petri_net.marking()
        print(f"✓ Initial marking: {marking}")
        
        # Check enabled transitions
        enabled = [t.name for t in ssm.petri_net.enabled_transitions()]
        print(f"✓ Enabled transitions: {enabled}")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_builder_pattern():
    """Test 3: Builder pattern for custom workflows"""
    print("\n" + "="*60)
    print("TEST 3: Builder Pattern for Custom Workflows")
    print("="*60)
    
    try:
        builder = SessionStateBuilder("analysis_workflow")
        builder.set_objective("Complete project analysis")
        
        # Add transitions
        builder.add_transition('start_analysis', ['objective_pending'], ['objective_in_progress'])
        builder.add_transition('complete_analysis', ['objective_in_progress'], ['objective_completed'])
        
        # Build
        ssm = builder.build()
        
        print(f"✓ Built custom workflow: {ssm}")
        
        # Get initial state
        state = ssm.get_state()
        print(f"✓ Initial objective: {state.objective}")
        
        # Check enabled transitions
        enabled = [t.name for t in ssm.petri_net.enabled_transitions()]
        print(f"✓ Initially enabled: {enabled}")
        
        # Fire start_analysis
        if 'start_analysis' in enabled:
            ssm.advance_objective('start_analysis')
            print(f"✓ Fired 'start_analysis' transition")
            
            state = ssm.get_state()
            print(f"✓ New marking: {ssm.petri_net.marking()}")
            
            enabled = [t.name for t in ssm.petri_net.enabled_transitions()]
            print(f"✓ Now enabled: {enabled}")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization():
    """Test 4: Petri Net visualization"""
    print("\n" + "="*60)
    print("TEST 4: Petri Net Visualization")
    print("="*60)
    
    try:
        # Create a session state manager
        ssm = SessionStateManager("visual_test")
        ssm.set_objective("Test visualization")
        
        # Create visualizer
        visualizer = PetriNetVisualizer(ssm.petri_net)
        
        # Generate ASCII art
        ascii_art = visualizer.to_ascii()
        
        print("\n" + ascii_art)
        print("\n✓ Visualization successful")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_controller_integration():
    """Test 5: MainController integration"""
    print("\n" + "="*60)
    print("TEST 5: MainController Integration")
    print("="*60)
    
    try:
        # Create MainController
        controller = MainController()
        
        print(f"✓ MainController created: {controller}")
        print(f"✓ Session manager: {controller.session_manager}")
        print(f"✓ Current session: {controller.session.name}")
        print(f"✓ Session state initialized: {controller.session_state}")
        
        # Test that session_state is None initially (will be created on first query)
        if controller.session_state is None:
            print(f"✓ Session state is None (will be created on first user query)")
        else:
            print(f"✓ Session state exists: {controller.session_state}")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_commands_integration():
    """Test 6: Commands integration"""
    print("\n" + "="*60)
    print("TEST 6: Commands Integration")
    print("="*60)
    
    try:
        # Create MainController
        controller = MainController()
        
        # Add commands
        controller.add_command(HelpCommand("help", controller))
        controller.add_command(NewCommand("new", controller))
        controller.add_command(PetriNetStatusCommand("status", controller))
        controller.add_command(PetriNetPrintCommand("petri-print", controller))
        
        print(f"✓ Commands added to controller")
        print(f"✓ Available commands: {[cmd.key for cmd in controller.get_commands()]}")
        
        # Test HelpCommand
        print("\n--- Testing HelpCommand ---")
        help_cmd = controller.find_command("help")
        result = help_cmd.run([])
        if result:
            result.apply()
            print(f"✓ HelpCommand executed")
        
        # Test NewCommand
        print("\n--- Testing NewCommand ---")
        new_cmd = controller.find_command("new")
        result = new_cmd.run(["test_session"])
        if result:
            result.apply()
            print(f"✓ NewCommand executed")
        
        # Test PetriNetStatusCommand (should show no active session)
        print("\n--- Testing PetriNetStatusCommand ---")
        status_cmd = controller.find_command("status")
        result = status_cmd.run([])
        if result:
            result.apply()
        else:
            print(f"✓ StatusCommand: No active session state (expected)")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_petri_net_generator():
    """Test 7: LLM Petri Net Generator (mock test)"""
    print("\n" + "="*60)
    print("TEST 7: LLM Petri Net Generator")
    print("="*60)
    
    try:
        from agentx.model.session.llm_petri_net_generator import LLMPetriNetGenerator
        
        generator = LLMPetriNetGenerator("agentx")
        print(f"✓ LLM Generator created: {generator}")
        print(f"  Note: Full LLM test requires API key")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PETRI NET SESSION STATE INTEGRATION TEST")
    print("="*60)
    
    tests = [
        ("SessionManager", test_session_manager),
        ("SessionStateManager", test_session_state_manager),
        ("Builder Pattern", test_builder_pattern),
        ("Visualization", test_visualization),
        ("MainController Integration", test_main_controller_integration),
        ("Commands Integration", test_commands_integration),
        ("LLM Generator", test_llm_petri_net_generator),
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
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
