# Integration Guide: Session State Management

## Overview

This guide shows how to integrate the Session State Management system into Agent-X.

## 1. Quick Integration (Recommended)

### Step 1: Import the Module

```python
# In src/controllers/main_controller/main_controller.py
from model.session import SessionStateManager
```

### Step 2: Add to MainController

```python
class MainController(IMainViewPartner):
    def __init__(self):
        # Existing initialization
        self.session = Session("test")
        if not self.session.create() or not self.session.is_created():
            raise Exception()
        self.database = SessionDatabase(self.session)
        
        # NEW: Add session state manager
        self.session_state = SessionStateManager(self.session.name)
        self.session_state.set_objective("Default objective")
```

### Step 3: Use in Commands

```python
def run_command(self, user_input: str):
    command_data = self.parser.parse(user_input)
    if not command_data:
        return
    
    # Update session state with command
    self.session_state.update_context("last_command", command_data.key)
    
    # Execute command
    command = self.find_command(command_data.key)
    if command:
        self.database.insert_history_entry(command_data.key)
        result = command.run(command_data.arguments)
        if result:
            result.apply()
```

## 2. Complete Integration Example

### Modified MainController

```python
# src/controllers/main_controller/main_controller.py

from controllers.chat_controller.chat_controller import ChatController
from controllers.main_controller.commands_base import Command
from controllers.main_controller.commands_parser import CommandParser
from views.main_view.main_view import MainView, IMainViewPartner
from model.session.session import Session
from model.session.session import SessionDatabase
from model.session import SessionStateManager  # NEW IMPORT


class MainController(IMainViewPartner):
    def __init__(self):
        self.commands: dict[str, Command] = {}
        self.parser = CommandParser()
        self.view = MainView(self)
        self.session = Session("test_2")
        
        if not self.session.create() or not self.session.is_created():
            raise Exception()
        
        self.database = SessionDatabase(self.session)
        
        # NEW: Session state management
        self.session_state = SessionStateManager(self.session.name)
        self.session_state.set_objective("Assist user with their tasks")
    
    def showChat(self, query: str | None):
        self.chat_controller = ChatController()
        
        # Update objective based on query
        if query:
            self.session_state.set_objective(query)
        
        self.chat_controller.show(query)
    
    def run(self):
        self.view.show()
        
        while True:
            user_input = self.view.capture_input()
            
            # Track interaction in session state
            self.session_state.update_context("last_input", user_input)
            
            self.run_command(user_input)
    
    def run_command(self, user_input: str):
        command_data = self.parser.parse(user_input)
        if not command_data:
            return
        
        command = self.find_command(command_data.key)
        if not command:
            self.view.print_response_error(f"Unknown command: {command_data.key}")
            return
        
        self.database.insert_history_entry(command_data.key)
        
        try:
            result = command.run(command_data.arguments)
            if result:
                result.apply()
                
            # Update session state after command execution
            self.session_state.update_context(
                "last_command_result", 
                "success" if result else "no_result"
            )
            
        except Exception as e:
            self.view.print_response_error(f"Command execution failed")
            self.session_state.update_context("last_error", str(e))
    
    def get_session_summary(self) -> dict:
        """Get current session state summary."""
        return self.session_state.to_dict()
    
    def set_user_objective(self, objective: str):
        """Set or update user objective."""
        self.session_state.set_objective(objective)
```

## 3. Custom Workflows

### Example: Analysis Workflow

```python
from model.session import SessionStateBuilder

def setup_analysis_workflow(self):
    """Set up a custom analysis workflow."""
    builder = SessionStateBuilder(f"{self.session.name}_analysis")
    
    builder.set_objective("Complete project analysis")
    
    # Define workflow
    builder.add_transition('start_analysis', 
                          ['objective_pending'], 
                          ['analyzing'])
    builder.add_transition('found_key_files', 
                          ['analyzing'], 
                          ['files_identified'])
    builder.add_transition('analyze_structure', 
                          ['files_identified'], 
                          ['structure_analyzed'])
    builder.add_transition('complete', 
                          ['structure_analyzed'], 
                          ['objective_completed'])
    
    self.analysis_manager = builder.build()
```

### Example: Multi-Step Task

```python
def setup_multistep_task(self):
    """Set up multi-step task workflow."""
    builder = SessionStateBuilder("multistep")
    
    builder.set_objective("Complete multi-step task")
    
    # Step 1: Initialize
    builder.add_transition('init', ['pending'], ['initialized'])
    
    # Step 2: Parallel tasks
    builder.add_transition('task_a', ['initialized'], ['task_a_done'])
    builder.add_transition('task_b', ['initialized'], ['task_b_done'])
    
    # Step 3: Finalize
    builder.add_transition('finalize', 
                          ['task_a_done', 'task_b_done'], 
                          ['completed'])
    
    self.task_manager = builder.build()
```

## 4. State Persistence

### Save State to Database

```python
# In SessionDatabase class
def save_session_state(self, state_dict: dict):
    """Save session state to database."""
    import json
    state_json = json.dumps(state_dict)
    
    query = """
    INSERT INTO session_state (state_json, created_at)
    VALUES (?, ?)
    """
    
    self._insert(query, [state_json, datetime.now(timezone.utc)])
```

### Load State from Database

```python
def load_session_state(self, session_id: str):
    """Load session state from database."""
    query = """
    SELECT state_json FROM session_state 
    WHERE session_id = ? 
    ORDER BY created_at DESC 
    LIMIT 1
    """
    
    result = self._select(query, [session_id])
    if result:
        import json
        return json.loads(result[0][0])
    return None
```

## 5. Command Examples

### Command: Set Objective

```python
class SetObjectiveCommand(Command):
    key = "set_objective"
    
    def run(self, arguments: list[str]) -> CommandResult | None:
        if not arguments:
            return None
        
        objective = " ".join(arguments)
        self.controller.session_state.set_objective(objective)
        
        return CommandResult(
            message=f"Objective set: {objective}",
            should_exit=False
        )
```

### Command: Show Status

```python
class ShowStatusCommand(Command):
    key = "status"
    
    def run(self, arguments: list[str]) -> CommandResult | None:
        state = self.controller.session_state.get_state()
        
        output = []
        output.append(f"Objective: {state.objective}")
        output.append(f"Status: {state.context['objective_status']}")
        output.append(f"Marking: {state.context['marking']}")
        
        return CommandResult(
            message="\n".join(output),
            should_exit=False
        )
```

### Command: Complete Objective

```python
class CompleteObjectiveCommand(Command):
    key = "complete"
    
    def run(self, arguments: list[str]) -> CommandResult | None:
        manager = self.controller.session_state
        
        # Fire completion transition
        if manager.petri_net.fire_transition('complete'):
            return CommandResult(
                message="Objective completed!",
                should_exit=False
            )
        else:
            return CommandResult(
                message="Cannot complete objective yet",
                should_exit=False
            )
```

## 6. Testing Integration

### Unit Test Example

```python
# tests/test_session_state.py
import unittest
from model.session import SessionStateManager

class TestSessionStateIntegration(unittest.TestCase):
    
    def test_set_objective(self):
        manager = SessionStateManager("test")
        manager.set_objective("Test objective")
        
        state = manager.get_state()
        self.assertEqual(state.objective, "Test objective")
        self.assertEqual(state.context['objective_status'], 'pending')
    
    def test_advance_objective(self):
        manager = SessionStateManager("test")
        manager.set_objective("Test")
        
        # Add transition
        manager.petri_net.add_transition('test_transition')
        
        # Fire transition
        result = manager.advance_objective('test_transition')
        self.assertTrue(result)
    
    def test_serialization(self):
        manager = SessionStateManager("test")
        manager.set_objective("Serialize test")
        
        state_dict = manager.to_dict()
        
        self.assertIn('objective', state_dict)
        self.assertIn('marking', state_dict)
        self.assertEqual(state_dict['objective'], "Serialize test")
```

## 7. UI Integration

### Console Output

```python
def print_session_state(manager: SessionStateManager):
    """Print session state to console."""
    state = manager.get_state()
    
    print("\n" + "="*50)
    print("SESSION STATE")
    print("="*50)
    print(f"Objective: {state.objective}")
    print(f"Status: {state.context['objective_status']}")
    print(f"Progress: {len([v for v in state.context['marking'].values() if v > 0])} steps")
    
    if state.context['enabled_transitions']:
        print(f"Next actions: {', '.join(state.context['enabled_transitions'])}")
    
    print("="*50 + "\n")
```

### Status Bar

```python
def update_status_bar(view, manager: SessionStateManager):
    """Update status bar with session state."""
    state = manager.get_state()
    status = state.context['objective_status']
    
    if status == 'completed':
        view.set_status("✓ Objective Complete")
    elif status == 'in_progress':
        view.set_status("⟳ In Progress")
    else:
        view.set_status("○ Pending")
```

## 8. Error Handling

### Graceful Degradation

```python
class SafeSessionStateManager:
    """Wrapper with error handling."""
    
    def __init__(self, manager: SessionStateManager):
        self.manager = manager
    
    def set_objective(self, objective: str):
        try:
            return self.manager.set_objective(objective)
        except Exception as e:
            print(f"Warning: Could not set objective: {e}")
            return False
    
    def advance_objective(self, transition: str):
        try:
            return self.manager.advance_objective(transition)
        except Exception as e:
            print(f"Warning: Could not advance: {e}")
            return False
```

## 9. Migration Path

### Phase 1: Basic Integration (Current)
- [x] Core implementation complete
- [ ] Add to MainController
- [ ] Basic commands

### Phase 2: Enhanced Features
- [ ] Database persistence
- [ ] Custom workflows
- [ ] UI integration

### Phase 3: Advanced Features
- [ ] State recovery
- [ ] Multi-session support
- [ ] Analytics

## 10. Checklist

Before deploying:

- [ ] Import statements added
- [ ] SessionStateManager initialized in MainController
- [ ] Objective set on session start
- [ ] State updated on command execution
- [ ] Error handling in place
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Performance acceptable

---

**Related Documents**:
- [README.md](./README.md) - Main proposal
- [TECHNICAL_DETAILS.md](./TECHNICAL_DETAILS.md) - Technical deep dive
