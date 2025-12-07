# Tasks: C-S Framework for Python

**Feature**: C-S Framework for Python
**Status**: Plan
**Spec**: [spec.md](spec.md)

## Phase 1: Setup
*Goal: Initialize project structure and dependencies.*

- [x] T001 Create project directory structure (`src/cs_framework`, `src/cs_gui`, `tests`, `src/examples`)
- [x] T002 Create `requirements.txt` with `rdflib`, `nicegui`, `networkx`, `pytest`
- [x] T003 Create `pytest.ini` for test configuration

## Phase 2: Foundational
*Goal: Establish shared contracts and base structures.*

- [x] T004 Create `src/cs_framework/logging/ontology.py` defining RDF namespace and constants
- [x] T005 Create `src/cs_framework/__init__.py` and subpackage `__init__.py` files

## Phase 3: User Story 1 - Define and Execute Independent Concepts
*Goal: Enable definition of Concepts and Synchronizations that can execute actions and update state.*
*Independent Test: Create two simple Concepts and one Synchronization. Trigger an action on Source and verify Target is updated.*

- [x] T006 [US1] Create `src/cs_framework/core/event.py` defining `Action`, `Event`, `EventPattern`, `ActionInvocation`, and `FailureEvent`
- [x] T007 [US1] Create `src/cs_framework/core/concept.py` implementing `Concept` base class
- [x] T008 [US1] Create `src/cs_framework/core/synchronization.py` implementing `Synchronization` class
- [x] T009 [US1] Create `src/cs_framework/engine/runner.py` for execution orchestration (implement recursion depth limit)
- [x] T010 [US1] Create `tests/unit/test_concept.py` to verify Concept state and action dispatch
- [x] T011 [US1] Create `tests/integration/test_sync_flow.py` to verify Synchronization between two Concepts

## Phase 4: User Story 2 - Generate Traceable Execution Logs
*Goal: Produce RDF/Turtle logs for all system executions to enable autonomous debugging.*
*Independent Test: Run the US1 test case and verify the output log file contains correct RDF triples.*

- [x] T012 [US2] Create `src/cs_framework/logging/logger.py` implementing `RDFLogger` with `rdflib` (support file and console output)
- [x] T013 [US2] Update `src/cs_framework/core/concept.py` to integrate logging in `dispatch` and `apply` (Implemented via Runner)
- [x] T014 [US2] Update `src/cs_framework/core/synchronization.py` to integrate logging in `execute` (Implemented via Runner)
- [x] T015 [US2] Create `tests/unit/test_logging.py` to verify Turtle output format and content

## Phase 5: User Story 3 - Visualize Execution State
*Goal: Provide a browser-based GUI to visualize the execution graph in real-time.*
*Independent Test: Load a generated log file into the GUI and verify the graph renders and updates.*

- [x] T016 [US3] Create `src/cs_gui/graph_loader.py` to parse Turtle logs into NetworkX/ECharts format
- [x] T017 [US3] Create `src/cs_gui/main.py` implementing the NiceGUI application structure
- [x] T018 [US3] Implement real-time log tailing and graph update logic in `src/cs_gui/main.py`

## Phase 6: Polish & Cross-Cutting Concerns
*Goal: Finalize documentation and provide usage examples.*

- [x] T019 Create `src/examples/simple_demo/concepts.py` with example Concepts for demonstration
- [x] T020 Create `src/examples/simple_demo/main.py` to run the full demo with logging and GUI
- [x] T021 Create `README.md` with installation and usage instructions

## Dependencies

1. **US1 (Core)**: Must be completed first to have a working system.
2. **US2 (Logging)**: Depends on US1 to have events to log.
3. **US3 (Visualization)**: Depends on US2 to generate the logs it visualizes.

## Parallel Execution Examples

- **Within US1**: `T006` (Event models) is a prerequisite, but `T007` (Concept) and `T008` (Synchronization) can be implemented in parallel once `T006` is agreed upon.
- **Within US3**: `T016` (Graph Loader) and `T017` (GUI Skeleton) can be implemented in parallel.

## Implementation Strategy

- **MVP (US1)**: Focus on getting the "Concept -> Sync -> Concept" flow working in memory first.
- **Traceability (US2)**: Add the RDF logging layer. This is critical for the "C-S" value proposition.
- **Visualization (US3)**: Build the GUI last, as it is a consumer of the logs.
