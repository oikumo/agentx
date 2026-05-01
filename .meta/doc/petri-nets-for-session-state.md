# Petri Nets for AgentX Session State Management

**Document ID**: AGENTX-PN-001  
**Purpose**: Explain Petri Nets and their application to representing semantic global state of user queries in AgentX  
**Audience**: Developers and AI agents working on AgentX session management  
**Status**: ✅ Active  
**Last Updated**: 2026-05-01  

---

## Executive Summary

This document explains **Petri Nets** as a mathematical formalism for modeling the semantic global state of complex user prompts in AgentX. By representing user queries as token flow through a network of places and transitions, we achieve:

- ✅ **Formal state tracking**: Mathematically rigorous session progression
- ✅ **Semantic representation**: User intent captured as net structure
- ✅ **Verifiable properties**: Can prove boundedness, liveness, deadlock-freedom
- ✅ **Adaptive workflows**: Dynamic net generation from user prompts
- ✅ **State persistence**: Sessions can be saved, restored, and analyzed

**Key Insight**: A user query like *"I want to analyze the project structure and document the findings"* becomes a Petri Net where tokens flow through places representing semantic states (analyze → document), with transitions representing state changes.

---

## 1. What is a Petri Net?

### 1.1 Basic Definition

A **Petri Net** is a mathematical modeling tool consisting of three components:

1. **Places** (circles ○): Hold tokens, represent states
2. **Transitions** (rectangles □): Fire when enabled, change state
3. **Arcs** (arrows →): Connect places to transitions, define flow

```
Example: Simple objective tracking

[objective_pending] ──(start)──> [objective_in_progress] ──(finish)──> [objective_completed]
     ● (1 token)                    □ (transition)              □ (transition)
                                    ○ (0 tokens)                ○ (0 tokens)
```

### 1.2 Formal Definition

A Petri Net is a tuple **PN = (P, T, A, M₀)** where:

- **P** = {p₁, p₂, ..., pₙ} is a finite set of **places**
- **T** = {t₁, t₂, ..., tₘ} is a finite set of **transitions**
- **A** ⊆ (P × T) ∪ (T × P) is a set of **arcs** (connections)
- **M₀** is the **initial marking** (token distribution)

**Rules**:
- Places and transitions are disjoint: P ∩ T = ∅
- Arcs only connect Place→Transition or Transition→Place
- A transition fires when all input places have sufficient tokens
- Firing consumes tokens from inputs and produces to outputs

### 1.3 Token Flow Mechanics

**Transition Firing Process**:

```python
def fire(transition):
    # 1. Check if enabled (all inputs have tokens)
    if not is_enabled(transition):
        return False
    
    # 2. Consume from inputs
    for place, weight in transition.inputs:
        place.tokens -= weight
    
    # 3. Produce to outputs
    for place, weight in transition.outputs:
        place.tokens += weight
    
    return True
```

**Example Flow**:

```
Initial State:
[ pending: 1 ]  [ in_progress: 0 ]  [ completed: 0 ]
      ●                 ○                  ○

Fire 'start' transition:
[ pending: 0 ]  [ in_progress: 1 ]  [ completed: 0 ]
      ○                 ●                  ○

Fire 'finish' transition:
[ pending: 0 ]  [ in_progress: 0 ]  [ completed: 1 ]
      ○                 ○                  ●
```

---

## 2. Petri Nets for User Query Semantics

### 2.1 Core Concept

A **user query** contains semantic intent that can be decomposed into:

1. **Objective**: What the user wants to achieve
2. **Workflow**: Steps to achieve the objective
3. **State**: Current progress through the workflow
4. **Transitions**: Actions that advance the state

**Example Query**: *"I want to analyze the project structure"*

**Semantic Decomposition**:
- **Objective**: "analyze the project structure"
- **Implied Workflow**: 
  1. Understand project layout
  2. Identify key components
  3. Document findings
- **State Model**: pending → analyzing → documenting → completed

### 2.2 Mapping Query to Petri Net

**Step 1: Extract Objective**

From user prompt: *"I want to analyze the project structure"*

Extracted objective: `"analyze the project structure"`

**Step 2: Identify Semantic States**

Based on objective type (analysis task), identify canonical states:

```python
states = [
    "analysis_pending",      # Initial state
    "understanding_layout",  # Step 1
    "identifying_components", # Step 2
    "documenting_findings",  # Step 3
    "analysis_completed"     # Final state
]
```

**Step 3: Define Transitions**

```python
transitions = [
    ("start_analysis", ["analysis_pending"], ["understanding_layout"]),
    ("layout_understood", ["understanding_layout"], ["identifying_components"]),
    ("components_identified", ["identifying_components"], ["documenting_findings"]),
    ("findings_documented", ["documenting_findings"], ["analysis_completed"])
]
```

**Step 4: Create Petri Net**

```
[analysis_pending] ──(start)──> [understanding_layout]
       ●                              ○
       
       ──(layout_understood)──> [identifying_components]
                                     ○
       
       ──(components_identified)──> [documenting_findings]
                                          ○
       
       ──(findings_documented)──> [analysis_completed]
                                        ○
```

### 2.3 Semantic Global State

The **global semantic state** of the query is represented by:

1. **Current Marking**: Which place has the token?
2. **Enabled Transitions**: What actions can be taken next?
3. **History**: Sequence of previous markings
4. **Objective**: The original user intent

**State Representation**:

```python
{
    "objective": "analyze the project structure",
    "current_marking": {
        "understanding_layout": 1,  # Token is here
        "analysis_pending": 0,
        "identifying_components": 0,
        "documenting_findings": 0,
        "analysis_completed": 0
    },
    "enabled_transitions": ["layout_understood"],
    "history": [
        {"marking": "analysis_pending", "timestamp": "T0"},
        {"marking": "understanding_layout", "timestamp": "T1"}
    ],
    "semantic_type": "analysis_task",
    "complexity": "medium"
}
```

---

## 3. Generating Petri Nets from User Prompts

### 3.1 Automatic Workflow Generation

AgentX can **dynamically generate** a Petri Net from a user prompt by:

1. **Parsing** the objective from natural language
2. **Classifying** the task type (analysis, implementation, debug, etc.)
3. **Selecting** a workflow template
4. **Instantiating** the Petri Net

**Example 1: Debug Task**

```
User: "I want to debug the login issue"
  ↓
Objective Extracted: "debug the login issue"
  ↓
Petri Net:
- Nodes: ["login_fail", "login_fail_tested", "login_fail_analyzed", "login_problem", "login_fixed"]
- Transitions: ["login_fail_test", "test_ready", "login_fail_cause_analysis", "analysis_ready", "solved", "solution_fail"]
- Edges:
  "login_fail" -> [login_fail_test] -> "login_fail_tested"
  "login_fail_tested" -> [test_ready] -> "login_problem"
  "login_fail" -> [login_fail_cause_analysis] -> "login_fail_analyzed"
  "login_fail_analyzed" -> [analysis_ready] -> "login_problem"
  "login_problem" -> [solved] -> "login_fixed"
  "login_problem" -> [solution_fail] -> "login_problem"
```

**Example 2: Analysis Task**

```
User: "I want to analyze the project structure"
  ↓
Objective Extracted: "analyze the project structure"
  ↓
Petri Net:
- Nodes: ["analysis_pending", "context_gathered", "structure_analyzed", "findings_documented", "analysis_completed"]
- Transitions: ["gather_context", "analyze_structure", "document_findings", "complete_analysis"]
- Edges:
  "analysis_pending" -> [gather_context] -> "context_gathered"
  "context_gathered" -> [analyze_structure] -> "structure_analyzed"
  "structure_analyzed" -> [document_findings] -> "findings_documented"
  "findings_documented" -> [complete_analysis] -> "analysis_completed"
```

**Example 3: Implementation Task**

```
User: "Add a new feature to upload files"
  ↓
Objective Extracted: "add file upload feature"
  ↓
Petri Net:
- Nodes: ["feature_pending", "approach_planned", "feature_implemented", "feature_tested", "feature_completed"]
- Transitions: ["plan_approach", "implement_feature", "test_feature", "finalize"]
- Edges:
  "feature_pending" -> [plan_approach] -> "approach_planned"
  "approach_planned" -> [implement_feature] -> "feature_implemented"
  "feature_implemented" -> [test_feature] -> "feature_tested"
  "feature_tested" -> [finalize] -> "feature_completed"
```

### 3.2 Workflow Templates

AgentX maintains a library of **workflow templates** for common task types. Each template defines the Petri Net structure using the format:

```
- Nodes: List of states (places)
- Transitions: List of actions that change state
- Edges: State -> [Transition] -> Next State
```

**Debug Workflow Template**:
```
- Nodes: ["issue_pending", "issue_reproduced", "cause_diagnosed", "fix_implemented", "fix_verified", "issue_resolved"]
- Transitions: ["reproduce", "diagnose", "implement_fix", "verify", "close"]
- Edges:
  "issue_pending" -> [reproduce] -> "issue_reproduced"
  "issue_reproduced" -> [diagnose] -> "cause_diagnosed"
  "cause_diagnosed" -> [implement_fix] -> "fix_implemented"
  "fix_implemented" -> [verify] -> "fix_verified"
  "fix_verified" -> [close] -> "issue_resolved"
```

**Analysis Workflow Template**:
```
- Nodes: ["analysis_pending", "context_gathered", "structure_analyzed", "findings_documented", "analysis_completed"]
- Transitions: ["gather_context", "analyze_structure", "document_findings", "complete"]
- Edges:
  "analysis_pending" -> [gather_context] -> "context_gathered"
  "context_gathered" -> [analyze_structure] -> "structure_analyzed"
  "structure_analyzed" -> [document_findings] -> "findings_documented"
  "findings_documented" -> [complete] -> "analysis_completed"
```

**Implementation Workflow Template**:
```
- Nodes: ["feature_pending", "approach_planned", "feature_implemented", "feature_tested", "feature_refined", "feature_completed"]
- Transitions: ["plan", "implement", "test", "refine", "finalize"]
- Edges:
  "feature_pending" -> [plan] -> "approach_planned"
  "approach_planned" -> [implement] -> "feature_implemented"
  "feature_implemented" -> [test] -> "feature_tested"
  "feature_tested" -> [refine] -> "feature_refined"
  "feature_refined" -> [finalize] -> "feature_completed"
```

### 3.3 Implementation Example

```python
from agentx.model.session import SessionStateManager, SessionStateBuilder

def create_session_from_prompt(user_prompt: str) -> SessionStateManager:
    """
    Generate a Petri Net session from a user prompt.
    
    Args:
        user_prompt: Natural language query from user
        
    Returns:
        SessionStateManager with generated Petri Net
    """
    # Step 1: Extract objective
    objective = extract_objective(user_prompt)
    
    # Step 2: Classify task type
    task_type = classify_task(objective)
    
    # Step 3: Get workflow template
    workflow = get_workflow_template(task_type)
    
    # Step 4: Build Petri Net
    builder = SessionStateBuilder("agentx_session")
    builder.set_objective(objective)
    
    # Add transitions from workflow
    for transition_name, inputs, outputs in workflow['transitions']:
        builder.add_transition(transition_name, inputs, outputs)
    
    # Build and return
    manager = builder.build()
    return manager

# Usage
user_prompt = "I want to analyze the project structure"
session_manager = create_session_from_prompt(user_prompt)

# Check state
state = session_manager.get_state()
print(f"Objective: {state.objective}")
print(f"Current state: {state.context['objective_status']}")
print(f"Enabled actions: {state.context['enabled_transitions']}")
```

---

## 4. Advanced Petri Net Features

### 4.1 Parallel Workflows

Some tasks have **parallel branches**:

```
User: "Analyze the codebase and write documentation"

Workflow:
               /──> [analyzing_code] ──\
[start] ──────<                         >──> [completed]
               \──> [writing_docs] ────/

Both branches must complete before final state.
```

**Petri Net Representation**:
```python
parallel_workflow = {
    "places": ["start", "analyzing_code", "writing_docs", "completed"],
    "transitions": [
        ("split", ["start"], ["analyzing_code", "writing_docs"]),
        ("code_done", ["analyzing_code"], ["sync"]),
        ("docs_done", ["writing_docs"], ["sync"]),
        ("merge", ["sync"], ["completed"])
    ]
}
```

### 4.2 Conditional Branches

**Choice pattern** - different paths based on conditions:

```
User: "Review the code for issues"

Workflow:
                /──> [minor_issues] ──> [document_issues]
[start] ───────<
                \──> [major_issues] ──> [plan_refactoring]
```

### 4.3 Loops and Iterations

**Loop pattern** - iterate until condition met:

```
[process] → [check_quality] ──(fail)──> [process]
                │
              (pass)
                ↓
          [completed]
```

### 4.4 Weighted Arcs

Some transitions require **multiple tokens**:

```python
# Requires 2 tokens in 'reviews' place to fire 'approve' transition
transition = Transition("approve")
transition.add_input(places["reviews"], weight=2)  # Needs 2 reviews
transition.add_output(places["approved"], weight=1)
```

---

## 5. Semantic Analysis with Petri Nets

### 5.1 State Properties

From the Petri Net structure, we can derive:

**Boundedness**: 
- Check: No place accumulates infinite tokens
- Meaning: Session won't grow unbounded
- Analysis: `is_bounded(net)` → True/False

**Liveness**:
- Check: All transitions can eventually fire
- Meaning: No dead ends in workflow
- Analysis: `is_live(net)` → True/False

**Deadlock-freedom**:
- Check: At least one transition always enabled
- Meaning: Session never gets stuck
- Analysis: `has_no_deadlocks(net)` → True/False

**Reachability**:
- Check: Can we reach state S from initial state?
- Meaning: Is this workflow outcome possible?
- Analysis: `is_reachable(net, target_state)` → True/False

### 5.2 Semantic Similarity

Compare two user queries by their Petri Net structures:

```python
def compare_workflows(net1, net2):
    """
    Compare semantic similarity of two Petri Nets.
    
    Returns similarity score 0.0 to 1.0
    """
    # Compare place sets
    place_similarity = jaccard(net1.places, net2.places)
    
    # Compare transition sets
    transition_similarity = jaccard(net1.transitions, net2.transitions)
    
    # Compare workflow depth
    depth_similarity = 1.0 - abs(net1.depth - net2.depth) / max_depth
    
    # Weighted average
    return 0.4 * place_similarity + 0.4 * transition_similarity + 0.2 * depth_similarity

# Example
query1 = "Analyze the project structure"
query2 = "Review the codebase organization"
similarity = compare_workflows(generate_net(query1), generate_net(query2))
print(f"Semantic similarity: {similarity:.2f}")  # Output: ~0.85
```

### 5.3 Progress Metrics

From the Petri Net marking, calculate:

**Completion Percentage**:
```python
def calculate_progress(net):
    """Calculate % completion based on token position."""
    total_places = len(net.places)
    current_place = get_place_with_token(net)
    current_index = net.places.index(current_place)
    return (current_index / total_places) * 100
```

**Estimated Steps Remaining**:
```python
def steps_remaining(net):
    """Count transitions to completion."""
    current_marking = net.marking()
    completed = current_marking.get('completed', 0) > 0
    
    if completed:
        return 0
    
    # Count transitions from current to end
    return len(net.remaining_transitions())
```

---

## 6. Practical Examples

### Example 1: Simple Query

```
User: "Show me the weather"
  ↓
Objective: "show the weather"
  ↓
Petri Net:
- Nodes: ["weather_pending", "weather_fetching", "weather_displayed", "weather_completed"]
- Transitions: ["fetch_weather", "display_weather", "complete"]
- Edges:
  "weather_pending" -> [fetch_weather] -> "weather_fetching"
  "weather_fetching" -> [display_weather] -> "weather_displayed"
  "weather_displayed" -> [complete] -> "weather_completed"
```

### Example 2: Complex Refactoring Task

```
User: "I want to refactor the authentication module to use OAuth2"
  ↓
Objective: "refactor authentication to OAuth2"
  ↓
Petri Net:
- Nodes: ["auth_pending", "current_auth_understood", "oauth2_researched", "migration_planned", "oauth2_implemented", "integration_tested", "deployed", "auth_completed"]
- Transitions: ["understand_current", "research_oauth2", "plan_migration", "implement_oauth2", "test_integration", "deploy", "complete"]
- Edges:
  "auth_pending" -> [understand_current] -> "current_auth_understood"
  "current_auth_understood" -> [research_oauth2] -> "oauth2_researched"
  "oauth2_researched" -> [plan_migration] -> "migration_planned"
  "migration_planned" -> [implement_oauth2] -> "oauth2_implemented"
  "oauth2_implemented" -> [test_integration] -> "integration_tested"
  "integration_tested" -> [deploy] -> "deployed"
  "deployed" -> [complete] -> "auth_completed"
```

### Example 3: Debug Session

```
User: "The login fails with error 500"
  ↓
Objective: "fix login 500 error"
  ↓
Petri Net:
- Nodes: ["error_pending", "error_reproduced", "logs_examined", "cause_identified", "fix_implemented", "fix_verified", "error_resolved"]
- Transitions: ["reproduce_error", "examine_logs", "identify_cause", "implement_fix", "verify_fix", "close"]
- Edges:
  "error_pending" -> [reproduce_error] -> "error_reproduced"
  "error_reproduced" -> [examine_logs] -> "logs_examined"
  "logs_examined" -> [identify_cause] -> "cause_identified"
  "cause_identified" -> [implement_fix] -> "fix_implemented"
  "fix_implemented" -> [verify_fix] -> "fix_verified"
  "fix_verified" -> [close] -> "error_resolved"
```

### Example 4: Parallel Workflow

```
User: "Analyze the codebase and write documentation"
  ↓
Objective: "analyze codebase and document"
  ↓
Petri Net:
- Nodes: ["task_pending", "codebase_analyzed", "documentation_written", "task_completed"]
- Transitions: ["analyze_codebase", "write_documentation", "complete_both"]
- Edges:
  "task_pending" -> [analyze_codebase] -> "codebase_analyzed"
  "task_pending" -> [write_documentation] -> "documentation_written"
  "codebase_analyzed" -> [complete_both] -> "task_completed"
  "documentation_written" -> [complete_both] -> "task_completed"
```

### Example 5: Loop/Retry Pattern

```
User: "Keep testing until the build passes"
  ↓
Objective: "get build to pass"
  ↓
Petri Net:
- Nodes: ["build_pending", "build_running", "build_passed", "build_failed", "build_completed"]
- Transitions: ["run_build", "pass", "fail", "retry"]
- Edges:
  "build_pending" -> [run_build] -> "build_running"
  "build_running" -> [pass] -> "build_passed"
  "build_running" -> [fail] -> "build_failed"
  "build_failed" -> [retry] -> "build_pending"
  "build_passed" -> [complete] -> "build_completed"
```

---

## 7. Implementation in AgentX

### 7.1 Core Classes

The AgentX implementation uses these classes:

**AdaptivePetriNet** (`src/agentx/model/session/adaptive_petri_net.py`):
```python
class AdaptivePetriNet:
    """Dynamic Petri net for session state."""
    
    def __init__(self, name: str):
        self.name = name
        self.places: dict[str, Place] = {}
        self.transitions: dict[str, Transition] = {}
        self.objective: str = ""
        self.state_history: list[dict] = []
    
    def set_objective(self, objective: str, initial_tokens: dict):
        """Set objective and initialize places."""
        
    def fire_transition(self, transition_name: str) -> bool:
        """Fire transition if enabled."""
        
    def marking(self) -> dict[str, int]:
        """Get current token distribution."""
        
    def enabled_transitions(self) -> list[Transition]:
        """Get list of enabled transitions."""
```

**SessionStateManager** (`src/agentx/model/session/session_state_manager.py`):
```python
class SessionStateManager:
    """High-level API for session state management."""
    
    def __init__(self, session_name: str):
        self.petri_net = AdaptivePetriNet(session_name)
    
    def set_objective(self, objective: str):
        """Set user objective."""
    
    def advance_objective(self, transition: str) -> bool:
        """Advance to next state."""
    
    def get_state(self) -> SessionState:
        """Get current semantic state."""
    
    def to_dict(self) -> dict:
        """Serialize state."""
```

### 7.2 Integration Points

**MainController Integration**:
```python
class MainController:
    def __init__(self):
        # Existing initialization
        self.session_manager = SessionManager()
        self.session = self.session_manager.get_current_session()
        
        # NEW: Session state with Petri Net
        self.session_state = SessionStateManager(self.session.name)
    
    def handle_user_query(self, query: str):
        """Process user query and update Petri Net state."""
        # Extract objective from first query
        if not self.session_state.get_state().objective:
            self.session_state.set_objective(query)
        
        # Continue with normal processing
        # ...
```

### 7.3 Usage Example

```python
from agentx.model.session import SessionStateManager

# Create session
manager = SessionStateManager("debug_session")

# Set objective from user query
manager.set_objective("Fix the login 500 error")

# Check initial state
state = manager.get_state()
print(f"Objective: {state.objective}")
print(f"Status: {state.context['objective_status']}")
# Output: Status: pending

# Advance through workflow
manager.advance_objective("reproduce")  # Fire 'reproduce' transition
state = manager.get_state()
print(f"Status: {state.context['objective_status']}")
# Output: Status: reproducing_error

# Check what's enabled
print(f"Next actions: {state.context['enabled_transitions']}")
# Output: Next actions: ['examine_logs']

# Serialize for persistence
state_dict = manager.to_dict()
```

---

## 8. Benefits of Petri Net Representation

### 8.1 Formal Properties

| Property | Benefit | AgentX Application |
|----------|---------|-------------------|
| **Boundedness** | Guaranteed finite states | Session won't explode |
| **Liveness** | No dead transitions | Always progress possible |
| **Reachability** | Can prove outcomes | Verify workflow completion |
| **Reversibility** | Can return to start | Undo operations |

### 8.2 Semantic Analysis

- **Intent Clarity**: Explicit objective representation
- **Progress Tracking**: Quantifiable advancement
- **Workflow Comparison**: Measure similarity between tasks
- **Bottleneck Detection**: Identify stuck transitions

### 8.3 Agent Coordination

- **State Sharing**: Pass Petri Net between agents
- **Handoff Support**: New agent continues from marking
- **Multi-agent Workflows**: Distribute transitions across agents

### 8.4 User Experience

- **Progress Visualization**: Show users where they are
- **Expectation Setting**: Display remaining steps
- **Transparency**: Users see the workflow structure

---

## 9. Limitations and Considerations

### 9.1 Limitations

1. **Complexity**: Large workflows become hard to visualize
2. **Rigidity**: Fixed structure may not fit all queries
3. **Overhead**: Maintaining state adds computational cost
4. **Learning Curve**: Developers need Petri Net understanding

### 9.2 Mitigations

1. **Abstraction**: Hide complexity from end users
2. **Templates**: Use pre-defined workflows for common patterns
3. **Optimization**: Efficient data structures for marking updates
4. **Documentation**: This document serves as reference

### 9.3 When NOT to Use Petri Nets

- Simple single-step queries (overkill)
- Queries with unclear objectives
- Highly dynamic workflows that change mid-execution
- Performance-critical paths where overhead matters

---

## 10. Future Enhancements

### Phase 1: Basic Integration ✅ (Current)
- [x] Core Petri Net implementation
- [x] SessionStateManager API
- [x] Basic workflow templates

### Phase 2: Advanced Features (Planned)
- [ ] Automatic workflow generation from prompts
- [ ] Workflow similarity detection
- [ ] Parallel branch support
- [ ] Conditional transitions

### Phase 3: Visualization (Future)
- [ ] ASCII art Petri Net viewer
- [ ] Interactive state explorer
- [ ] Progress bar from marking
- [ ] Historical replay

### Phase 4: Persistence (Future)
- [ ] Database storage of markings
- [ ] Session state recovery
- [ ] Cross-session analysis
- [ ] Workflow mining from history

---

## 11. Quick Reference

### Creating a Simple Petri Net

```python
from agentx.model.session import SessionStateManager

# Basic usage
manager = SessionStateManager("my_session")
manager.set_objective("My user objective")

# Advance state
manager.advance_objective("transition_name")

# Get current state
state = manager.get_state()
print(f"Status: {state.context['objective_status']}")
```

### Custom Workflow

```python
from agentx.model.session import SessionStateBuilder

# Build custom workflow
builder = SessionStateBuilder("custom")
builder.set_objective("Custom task")
builder.add_transition('step1', ['pending'], ['step1_done'])
builder.add_transition('step2', ['step1_done'], ['completed'])
manager = builder.build()

# Execute
manager.advance_objective('step1')
manager.advance_objective('step2')
```

### Checking State

```python
state = manager.get_state()

# Current objective
print(state.objective)

# Current status
print(state.context['objective_status'])  # pending|in_progress|completed

# Available actions
print(state.context['enabled_transitions'])

# Is complete?
print(manager.is_complete())
```

---

## 12. Glossary

| Term | Definition |
|------|-----------|
| **Place** | Node in Petri Net that holds tokens; represents a state |
| **Transition** | Node that fires when enabled; represents an action |
| **Token** | Marker that flows through the net; represents state |
| **Marking** | Distribution of tokens across places; current state |
| **Arc** | Connection between place and transition |
| **Enabled** | Transition can fire (all inputs have tokens) |
| **Fire** | Execute a transition (consume/produce tokens) |
| **Workflow** | Sequence of states and transitions |
| **Objective** | User's goal extracted from query |

---

## References

- **Implementation**: `src/agentx/model/session/`
- **Proposal**: `.meta/experiments/archive-2024-agent-x-session-state-proposal/`
- **Knowledge Base**: Entries PAT-F18D, PAT-2802, PAT-4F63
- **Petri Net Theory**: Wikipedia - Petri net, "Petri Nets: An Introduction" by Reisig

---

**Document Status**: ✅ Active  
**Next Review**: After Phase 2 implementation  
**Maintained By**: AgentX Development Team
