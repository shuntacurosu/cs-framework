# C-S Framework Specification

## 1. Core Architecture
The C-S Framework implements the Concept-Synchronization Constitution. It separates software into two distinct layers:
- **Concepts**: Independent units of state and behavior.
- **Synchronization**: The wiring that connects Concepts.

### 1.1 Concept
A Concept is a class inheriting from `cs_framework.core.concept.Concept`.
- **State**: Private dictionary `_state`.
- **Actions**: Methods that modify state.
- **Events**: Signals emitted when state changes.
- **Schema**: Events must be defined using Pydantic models for type safety.

### 1.2 Synchronization
Defined in YAML, Synchronizations map an Event from one Concept to an Action in another.
- **When**: Source Concept + Event Name.
- **Then**: Target Concept + Action Name.

### 1.3 Runner
The engine that executes the application.
- Manages the Event Queue.
- Dispatches Actions.
- Logs execution to RDF (`execution.ttl`).

## 2. Event System
Events are the only way Concepts communicate.
- **Payload**: Data carried by the event (Pydantic Model).
- **Causal Link**: ID of the event/action that caused this event.

## 3. Skills (Tooling)
The framework includes AI-native tools designed to assist LLMs:
- **Architect**: Generates Concept skeletons from natural language.
- **Linter**: Static analysis for graph integrity (detects dead ends, undefined actions).
- **Fuzzer**: Scenario-based testing for bug reproduction.
- **Debugger**: SPARQL-based log analysis for root cause explanation.

## 4. Advanced Features
- **Invariants**: Runtime checks for consistency (e.g., "Score cannot be negative").
- **Hot-Swap**: Reloading Synchronization rules at runtime without restarting.
- **Shadow Mode**: Parallel execution of two Runners to detect state divergence.
- **Distributed Mesh**: Cross-process event propagation using `EventBridge`.

## 5. Development Workflow Integration

### 5.1 Spec-Kit Integration
The framework provides native integration with [Spec-Kit](https://github.com/spec-kit/spec-kit) to enforce architectural constraints during AI-assisted development.

- **Constitution Injection**: Automatically injects CSFW rules into the project's `constitution.md`.
- **Template Modification**: Updates `plan.md` and `tasks.md` templates to guide the AI towards using `csfw scaffold` and `csfw lint`.
- **Command**: `csfw integrate-speckit` (or `python -m cs_framework.cli integrate-speckit`).

This ensures that any AI agent working on the project adheres to the Concept-Synchronization pattern by default.
