# Data Model: C-S Framework for Python

**Feature**: C-S Framework for Python
**Date**: 2025-12-07 (Updated based on Design Review)

## Core Entities (Python Classes)

### Concept
The fundamental unit of modularity.
- **Attributes**:
    - `id` (UUID): Unique identifier.
    - `name` (str): Human-readable name.
    - `_state` (dict): Internal state data (private).
- **Methods**:
    - `dispatch(action_name, payload)`: Execute an action.
    - `apply(event)`: Update state based on event.
    - `get_state_snapshot()`: Return a read-only copy of the current state.

### Synchronization
The unit of composition, implementing the "When-Where-Then" pattern.
- **Attributes**:
    - `id` (UUID): Unique identifier.
    - `name` (str): Human-readable name.
    - `when` (EventPattern): Defines the triggering event (Source Concept + Event Name).
    - `where` (Callable): Optional condition function. Receives global state snapshot, returns boolean.
    - `then` (List[ActionInvocation]): List of actions to execute if condition passes.
- **Methods**:
    - `evaluate(event, global_state)`: Check if event matches `when` and `where` condition passes.
    - `execute(event)`: Returns the list of `ActionInvocation`s to be dispatched.

### EventPattern
Helper to define the "When".
- **Attributes**:
    - `source_concept` (str/Concept): The concept to listen to.
    - `event_name` (str): The specific event name.

### ActionInvocation
Helper to define the "Then".
- **Attributes**:
    - `target_concept` (str/Concept): The concept to invoke.
    - `action_name` (str): The action to perform.
    - `payload_mapper` (Callable): Function to transform event payload into action payload.

### Action / Event
Represents a change in the system.
- **Attributes**:
    - `id` (UUID): Unique identifier.
    - `name` (str): Name of the action/event.
    - `payload` (dict): Data associated with the action.
    - `timestamp` (datetime): When it occurred.
    - `causal_link` (UUID): ID of the Sync or Action that caused this.
    - `status` (str): "Success" or "Error".

## RDF Ontology (Logging Schema)

The log file will use the following RDF schema to represent execution traces.

**Namespace**: `cs: <http://cs-framework.org/schema/>`

### Classes
- `cs:Concept`: Represents a Concept instance.
- `cs:Synchronization`: Represents a Synchronization rule.
- `cs:Action`: Represents an action execution.
- `cs:Event`: Represents an event emitted after an action.
- `cs:ActionInvocation`: Represents the definition of an action call within a Sync.

### Properties
- `cs:hasName`: Name of the entity.
- `cs:hasState`: JSON string representation of state (simplified).
- `cs:belongsTo`: Links Action/Event to a Concept.
- `cs:triggeredBy`: Links Action to the Synchronization or User that triggered it.
- `cs:causedBy`: Links Synchronization execution to the Event that triggered it.
- `cs:invokes`: Links Synchronization to the ActionInvocations it contains (definition level).
- `cs:hasCondition`: Description of the 'where' clause (optional, string representation).
- `cs:status`: Status of the action (Success/Error).

## Graph Visualization Model (GUI)

The GUI will map RDF entities to Graph nodes/edges.

### Nodes
- **Type**: Concept
    - **Visual**: Large circle / Cluster.
- **Type**: Action/Event
    - **Visual**: Small dot inside or near Concept. Color-coded by Status (Green=Success, Red=Error).

### Edges
- **Type**: Synchronization
    - **Visual**: Directed arrow from Event (Source) to Action (Target).
    - **Label**: Sync Name.
- **Type**: Causal
    - **Visual**: Dashed line showing `triggeredBy`.
