#!/usr/bin/env python3
"""
Test the isolated SessionPetriNet module.

This test verifies that the SessionPetriNet module works correctly
as an isolated, self-contained interface for session state management.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the isolated module directly
from agentx.model.session.session_petri_net import (
    SessionPetriNet,
    create_from_objective,
    create_session_petri_net,
    AdaptivePetriNet,
    Place,
    Transition
)


def test_basic_creation():
    """Test 1: Basic creation"""
    print('Test 1: Create SessionPetriNet')
    petri = SessionPetriNet('test_session')
    print(f'✓ Created: {petri}')
    assert petri.session_name == 'test_session'
    return petri


def test_set_objective(petri):
    """Test 2: Set objective"""
    print('\nTest 2: Set objective')
    petri.set_objective('Analyze project structure')
    state = petri.get_state()
    print(f'✓ Objective: {state.objective}')
    print(f'✓ Status: {state.context["objective_status"]}')
    assert state.objective == 'Analyze project structure'
    assert state.context['objective_status'] == 'pending'
    return state


def test_initial_state(petri):
    """Test 3: Check initial state"""
    print('\nTest 3: Check initial state')
    print(f'✓ Marking: {petri.get_marking()}')
    print(f'✓ Enabled transitions: {petri.get_enabled_transitions()}')
    marking = petri.get_marking()
    assert 'objective_pending' in marking
    assert marking['objective_pending'] == 1
    assert marking['objective_in_progress'] == 0
    assert marking['objective_completed'] == 0


def test_fire_transition(petri):
    """Test 4: Fire transition"""
    print('\nTest 4: Fire transition')
    success = petri.fire('start')
    print(f'✓ Fire "start" transition: {success}')
    state = petri.get_state()
    print(f'✓ New status: {state.context["objective_status"]}')
    assert success
    assert state.context['objective_status'] == 'in_progress'


def test_convenience_function():
    """Test 5: Convenience function"""
    print('\nTest 5: Convenience function')
    petri2 = create_from_objective('Test objective', 'test2')
    print(f'✓ Created with objective: {petri2.get_state().objective}')
    assert petri2.get_state().objective == 'Test objective'
    
    petri3 = create_session_petri_net('test3')
    print(f'✓ Created session: {petri3.session_name}')
    assert petri3.session_name == 'test3'


def test_completion(petri):
    """Test 6: Check completion"""
    print('\nTest 6: Check completion')
    print(f'✓ Is complete: {petri.is_complete()}')
    assert not petri.is_complete()
    
    # Fire finish transition
    petri.fire('finish')
    print(f'✓ Is complete after finish: {petri.is_complete()}')
    assert petri.is_complete()


def test_advanced_operations():
    """Test 7: Advanced operations"""
    print('\nTest 7: Advanced operations')
    petri = SessionPetriNet('advanced_test')
    petri.set_objective('Custom workflow')
    
    # Add custom place
    petri.add_place('custom_place', tokens=1)
    print(f'✓ Added custom place')
    marking = petri.get_marking()
    assert 'custom_place' in marking
    assert marking['custom_place'] == 1
    
    # Add custom transition
    petri.add_transition('custom_transition')
    print(f'✓ Added custom transition')
    
    # Serialize to dict
    data = petri.to_dict()
    print(f'✓ Serialized keys: {list(data.keys())}')
    assert 'session_name' in data
    assert 'objective' in data
    assert 'marking' in data


def test_core_components():
    """Test 8: Core Petri net components"""
    print('\nTest 8: Core Petri net components')
    
    # Test Place
    place = Place('test_place', tokens=2)
    print(f'✓ Place: {place}')
    assert place.name == 'test_place'
    assert place.tokens == 2
    
    # Test Transition
    transition = Transition('test_transition')
    print(f'✓ Transition: {transition}')
    assert transition.name == 'test_transition'
    
    # Test AdaptivePetriNet
    net = AdaptivePetriNet('test_net')
    net.add_place('p1', tokens=1)
    net.add_transition('t1')
    print(f'✓ AdaptivePetriNet: {net.name}')
    assert net.name == 'test_net'


def main():
    """Run all tests."""
    print('=' * 60)
    print('Testing Isolated SessionPetriNet Module')
    print('=' * 60)
    
    try:
        # Test 1: Basic creation
        petri = test_basic_creation()
        
        # Test 2: Set objective
        test_set_objective(petri)
        
        # Test 3: Initial state
        test_initial_state(petri)
        
        # Test 4: Fire transition
        test_fire_transition(petri)
        
        # Test 5: Convenience functions
        test_convenience_function()
        
        # Test 6: Completion
        petri2 = SessionPetriNet('test_complete')
        petri2.set_objective('Test completion')
        test_completion(petri2)
        
        # Test 7: Advanced operations
        test_advanced_operations()
        
        # Test 8: Core components
        test_core_components()
        
        print('\n' + '=' * 60)
        print('✅ All tests passed!')
        print('=' * 60)
        return True
        
    except Exception as e:
        print(f'\n❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
