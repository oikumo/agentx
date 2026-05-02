# Systemic Application of Petri Nets in Large-Scale Software Lifecycle Management  
## Planning, Global State Analysis, and Dynamic Monitoring

Large-scale software engineering project management faces challenges of exponential complexity, where task concurrency, geographically distributed teams, and shared resource management demand more rigorous frameworks than those offered by traditional project management.

In this context, Petri nets emerge as a mathematical and graphical modeling language with precise execution semantics, ideal for describing distributed systems and complex business processes.

Unlike industry standards such as Gantt or PERT, which often lack a rigorous mathematical definition for concurrency control, Petri nets enable not only visual representation but also formal verification of critical properties such as deadlock-freedom, task liveness, and workflow soundness.

---

## Methodological Evolution: From Static Programming to Discrete Event Modeling

Modern software development has outgrown the capabilities of static planning tools.

- **Gantt charts**: Useful for simple scheduling but weak in dynamic monitoring.  
- **PERT**: Focused on time estimation and critical path but limited in scalability.

Petri nets, as discrete event dynamic systems, model concurrent and asynchronous behavior. The system state depends on token distribution across places and transitions, allowing non-deterministic evolution.

---

## Mathematical Foundations and Structure of Petri Nets

A Petri net is defined as:

$$
PN = (P, T, F, W, M_0)
$$

Where:

- **P**: Set of places (states)  
- **T**: Set of transitions (events)  
- **F**: Directed arcs  
- **W**: Weight function  
- **M₀**: Initial marking  

---

## Firing Rule and System Dynamics

A transition fires if all input places contain sufficient tokens:

$$
M'(p) = M(p) - W(p,t) + W(t,p)
$$

This enables accurate tracking of workflow execution.

---

## Project Planning with Workflow Nets (WF-nets)

WF-nets model lifecycle processes and must:

1. Have a single input place  
2. Have a single output place  
3. Ensure all nodes lie on a path between them  

### Control Patterns

| Pattern | Description |
|--------|------------|
| Sequence | Dependent tasks |
| Parallelism (AND-split) | Simultaneous tasks |
| Synchronization (AND-join) | Merge dependencies |
| Selection (OR-split) | Decision branching |
| Iteration | Loops (e.g., bug fixing) |

---

## Global State Analysis and Soundness Verification

Using the **reachability graph**, we analyze all possible states.

### Soundness Criteria

- **Option to complete**: Final state is always reachable  
- **Proper completion**: No leftover tokens  
- **No dead transitions**: All tasks can execute  

---

## Bottleneck Detection and Temporal Analysis

With **Timed Petri Nets**, we compute:

- Earliest Start (ES)  
- Earliest Finish (EF)  
- Latest Start (LS)  
- Latest Finish (LF)  
- Total Float (TF) → identifies critical path  

---

## Resource Management and Deadlock Prevention

Resources are modeled as token-based places:

- Developers → availability tokens  
- Servers → capacity-limited places  
- Locks → single-token places  

### Deadlock Detection

- **Siphons**: Sets of places that may become empty  
- Empty siphons → deadlock  
- Solution: control places to maintain token flow  

---

## Monitoring: The Token Game in DevOps

Real-world events trigger transitions:

| Event | Effect |
|------|--------|
| Branch creation | Start task |
| Commit | Progress update |
| Merge request | Review phase |
| CI/CD failure | Return to fix stage |
| Deployment | Completion |

---

## PNML and Visualization Tools

PNML (XML standard) enables interoperability between tools:

- CPN Tools  
- Python-based frameworks  

Used for dashboards and real-time visualization.

---

## Practical Example: CI/CD Pipeline Modeling

Pipeline modeled as:
