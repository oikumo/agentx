---
name: mermaid-diagrammer
description: Generate, update, and validate all UML artifacts (Sequence, Class, State, ER, Component, Deployment, and Requirement diagrams) using precise Mermaid.js syntax.
license: MIT
compatibility: opencode
metadata:
  purpose: universal-uml-modeling
  version: 2.0.0
---

## What I do
- **UML Artifact Generation:** Translate software architectures into structurally sound UML diagrams using Mermaid.js syntax.
- **Reverse-Engineer Code to UML:** Analyze classes, database schemas, state machines, and API interactions to generate corresponding UML Class, ER, State, or Sequence diagrams.
- **Multi-Diagram Documentation:** Keep system documentation synchronized by embedding relevant behavioral and structural diagrams into `README.md` or dedicated architecture folders.

## Supported UML & Modeling Artifacts
1. **Structural Diagrams:** Class Diagrams (`classDiagram`), Entity-Relationship (`erDiagram`), Component/Deployment maps (built cleanly via `flowchart`).
2. **Behavioral Diagrams:** Sequence (`sequenceDiagram`), State Machines (`stateDiagram-v2`), User Journeys (`userJourney`).
3. **Project & Lifecycle Diagrams:** Gantt charts (`gantt`), Requirement tracking (`requirementDiagram`), Git branching workflows (`gitGraph`).

## Strict Syntax & Relationship Guardrails
When executing this skill, you must match the exact Mermaid syntax rules for the chosen UML artifact to prevent rendering errors:

### 1. Class Diagrams (`classDiagram`)
- Use precise relationship arrows. Do not hallucinate standard flowchart arrows:
  - **Inheritance/Generalization:** `<|--` (e.g., `Vehicle <|-- Car`)
  - **Composition:** `*--` (e.g., `Company *-- Department`)
  - **Aggregation:** `o--` (e.g., `Library o-- Book`)
  - **Association:** `-->` (e.g., `Customer --> Order`)
- Define visibility explicitly: `+` (Public), `-` (Private), `#` (Protected), `~` (Package/Internal).
- Format methods with parentheses: `+getName() String`.

### 2. Sequence Diagrams (`sequenceDiagram`)
- Use explicit participants where typing matters: `participant Alice as User`.
- Use correct arrow styles for message types:
  - **Synchronous call:** `->>` (Solid line, solid arrowhead)
  - **Asynchronous call:** `->` (Solid line, open arrowhead)
  - **Reply/Return message:** `-->>` (Dashed line, solid arrowhead)
- Always pair structural blocks properly: `alt/else/end`, `opt/end`, and `loop/end`.

### 3. State Diagrams (`stateDiagram-v2`)
- Always use the modern `stateDiagram-v2` definition rather than the legacy `stateDiagram`.
- Define start and end points explicitly using `[*]`.
- Use the `state "Description" as stateId` syntax for states with long or complex names.

### 4. Entity-Relationship Diagrams (`erDiagram`)
- Use exact cardinality notations:
  - **Exactly one:** `||`
  - **Zero or many:** `o{`
  - **One or many:** `|{`
- Format attributes inside blocks with their data types: `string username PK`.

### 5. Component & Deployment Diagrams (via `flowchart`)
- Because Mermaid lacks a dedicated deployment primitive, use `flowchart TD` or `flowchart LR`.
- Utilize structural boundaries using `subgraph` to visually isolate Clusters, Nodes, Pods, or logical Tiers.
- Style external actors or hardware boundaries using distinct node shapes (e.g., `nodeId[\"Hardware Container\"/]`).

## Workflow Execution
1. **Identify the Artifact:** Determine which UML artifact best addresses the user's request (e.g., State diagram for a payment gateway, Class diagram for an OOP refactor).
2. **Scan Scope:** Read the files or directories indicated to map classes, properties, or execution paths.
3. **Validate Syntax:** Review the output against the specific syntax rules listed above before outputting the markdown block.
4. **Deliver Clean Markdown:** Output the diagram wrapped inside a standard code block labeled `mermaid`. Do not inject prose or inline explanations inside the code block itself.