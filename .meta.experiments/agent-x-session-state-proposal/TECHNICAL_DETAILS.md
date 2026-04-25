# Technical Details: Session State with Adaptive Petri Nets

## 1. Petri Net Fundamentals

### What is a Petri Net?

A Petri net is a mathematical modeling tool consisting of:
- **Places**: Hold tokens (represent state)
- **Transitions**: Fire when enabled (change state)
- **Arcs**: Connect places to transitions (define flow)

### Our Implementation

```python
# Basic structure
Place(name="objective_pending", tokens=1)      # Initial state
Place(name="objective_in_progress", tokens=0)  # Working state
Place(name="objective_completed", tokens=0)    # Final state

Transition(name="start")  # Moves token from pending to in_progress
Transition(name="finish") # Moves token from in_progress to completed
```

## 2. Adaptive Features

### Dynamic Structure
```python
# Add places dynamically
manager.petri_net.add_place("custom_state", tokens=0)

# Add transitions dynamically
manager.petri_net.add_transition("custom_transition")

# Add arcs to connect
manager.petri_net.add_arc(place, transition, weight=1)
```

### Objective-Driven
```python
# Set objective - automatically creates initial places
manager.set_objective("Analyze project")

# Token flow represents objective progress
# pending (1) -> in_progress (1) -> completed (1)
```

## 3. State Representation

### Marking (Token Distribution)
```python
marking = manager.petri_net.marking()
# Example: {'objective_pending': 0, 
#           'objective_in_progress': 1, 
#           'objective_completed': 0}
```

### Enabled Transitions
```python
enabled = manager.petri_net.enabled_transitions()
# Returns list of transitions that can fire
```

### State History
```python
history = manager.get_history()
# List of all previous markings
```

## 4. Token Flow Mechanics

### Transition Firing
```python
# 1. Check if enabled (all input places have tokens)
if transition.is_enabled():
    # 2. Consume from inputs
    for place, weight in transition.inputs.items():
        place.tokens -= weight
    
    # 3. Produce to outputs
    for place, weight in transition.outputs.items():
        place.tokens += weight
```

### Example Flow
```
Initial:  pending=1, in_progress=0, completed=0
          [●]      [ ]          [ ]
          
Fire 'start':
          [ ]      [●]          [ ]
          pending=0, in_progress=1, completed=0
          
Fire 'finish':
          [ ]      [ ]          [●]
          pending=0, in_progress=0, completed=1
```

## 5. Class Hierarchy

```
AdaptivePetriNet
├── Places: dict[str, Place]
├── Transitions: dict[str, Transition]
├── objective: str
└── state_history: list[dict]

SessionStateManager
└── petri_net: AdaptivePetriNet
    ├── set_objective()
    ├── advance_objective()
    ├── get_state()
    └── to_dict()

SessionStateBuilder
└── Builds SessionStateManager with custom workflow
```

## 6. Data Structures

### SessionState
```python
@dataclass
class SessionState:
    objective: str
    context: dict[str, Any]
    created_at: str
    updated_at: str
```

### Serialized State
```python
{
    "session_name": "test_session",
    "objective": "Analyze project",
    "context": {
        "marking": {"objective_pending": 0, ...},
        "objective_status": "in_progress",
        "enabled_transitions": ["finish"]
    },
    "marking": {"objective_pending": 0, ...},
    "enabled_transitions": ["finish"],
    "is_complete": False,
    "created_at": "2026-04-25T19:27:09.828724+00:00",
    "updated_at": "2026-04-25T19:27:09.828731+00:00"
}
```

## 7. Advanced Usage

### Custom Workflow Definition
```python
builder = SessionStateBuilder("complex_workflow")
builder.set_objective("Multi-step analysis")

# Define multi-step workflow
builder.add_transition('step1', ['pending'], ['step1_done'])
builder.add_transition('step2', ['step1_done'], ['step2_done'])
builder.add_transition('step3', ['step2_done'], ['completed'])

manager = builder.build()

# Execute workflow
manager.advance_objective('step1')
manager.advance_objective('step2')
manager.advance_objective('step3')
```

### Parallel Transitions
```python
# Multiple transitions can be enabled simultaneously
builder.add_transition('parallel_a', ['start'], ['intermediate'])
builder.add_transition('parallel_b', ['start'], ['intermediate'])

# Either can fire first (non-deterministic)
```

### Weighted Arcs
```python
# Arcs can have weights (multiple tokens)
manager.petri_net.add_arc(place, transition, weight=2)
# Requires 2 tokens to fire
```

## 8. Verification Properties

### Boundedness
- Check: No place accumulates infinite tokens
- Our net: Always bounded (finite places, conservative)

### Liveness
- Check: All transitions can eventually fire
- Our net: Live if no deadlocks

### Deadlock-freedom
- Check: Always at least one transition enabled
- Our net: Deadlock-free by design (linear flow)

### Reversibility
- Check: Can return to initial state
- Our net: Not reversible (by design - objectives are progressive)

## 9. Performance Characteristics

| Operation | Complexity | Notes |
|-----------|------------|-------|
| `set_objective()` | O(1) | Creates initial places |
| `advance_objective()` | O(p) | p = number of arcs |
| `get_state()` | O(n) | n = number of places |
| `to_dict()` | O(n) | Serialization |
| `is_enabled()` | O(1) | Per transition |
| `fire()` | O(1) | Constant time |

## 10. Thread Safety

**Current Status**: Not thread-safe

**Recommendation**: Use locks if concurrent access needed:
```python
import threading

class ThreadSafeSessionStateManager(SessionStateManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = threading.Lock()
    
    def advance_objective(self, transition):
        with self._lock:
            return super().advance_objective(transition)
```

## 11. Memory Footprint

- **Base overhead**: ~50 KB (Python runtime)
- **Per session**: ~1 KB (state + history)
- **History**: Grows with each transition (configurable limit)

## 12. Extension Points

### Custom Place Types
```python
class TimedPlace(Place):
    def __init__(self, name, tokens=0, timeout=0):
        super().__init__(name, tokens)
        self.timeout = timeout
```

### Custom Transition Logic
```python
class ConditionalTransition(Transition):
    def __init__(self, name, condition):
        super().__init__(name)
        self.condition = condition
    
    def is_enabled(self):
        return super().is_enabled() and self.condition()
```

### Custom Analysis
```python
from model.session.adaptive_petri_net import AdaptivePetriNet

def analyze_session_net(net: AdaptivePetriNet):
    # Check for deadlocks
    # Analyze token flow
    # Generate report
    pass
```

## 13. Debugging Tips

### Inspect Current State
```python
state = manager.get_state()
print(f"Objective: {state.objective}")
print(f"Marking: {state.context['marking']}")
print(f"Enabled: {state.context['enabled_transitions']}")
```

### View History
```python
history = manager.get_history()
for i, step in enumerate(history):
    print(f"Step {i}: {step['marking']}")
```

### Debug Transition Firing
```python
transition_name = 'start'
if transition_name in manager.petri_net.transitions:
    t = manager.petri_net.transitions[transition_name]
    print(f"Transition {transition_name}:")
    print(f"  Inputs: {t.inputs}")
    print(f"  Outputs: {t.outputs}")
    print(f"  Enabled: {t.is_enabled()}")
```

## 14. Common Patterns

### Sequential Workflow
```python
pending -> step1 -> step2 -> step3 -> completed
```

### Parallel Workflow
```python
       /-> step_a ->\
start                -> completed
       \-> step_b ->/
```

### Choice Pattern
```python
       /-> path_a
start
       \-> path_b
```

### Loop Pattern
```python
start -> process -> check -> (if fail) -> process
                      -> (if pass) -> completed
```

---

**Next**: See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for integration instructions.
