# Research: C-S Framework for Python

**Feature**: C-S Framework for Python
**Date**: 2025-12-06

## Decisions

### 1. GUI Framework: NiceGUI

- **Decision**: Use **NiceGUI** for the visualization tool.
- **Rationale**:
    - **Real-time capabilities**: NiceGUI has built-in WebSocket support and a simple `ui.timer` mechanism that makes "tailing" a log file and pushing updates to the client extremely easy and performant.
    - **Python-centric**: It allows building the entire UI in Python without writing JavaScript, which aligns with the user's request for a Python framework.
    - **Graph Support**: It has built-in support for Apache ECharts (`ui.echart`), which is powerful enough for network graphs.
- **Alternatives Considered**:
    - **Streamlit**: Very popular but its execution model (rerun script on every interaction) makes real-time updates (like tailing a log) inefficient and prone to flickering.
    - **Dash**: Powerful but has a steeper learning curve and requires more boilerplate for simple real-time updates compared to NiceGUI.

### 2. Graph Visualization Library: Apache ECharts (via NiceGUI)

- **Decision**: Use **Apache ECharts** via `ui.echart`.
- **Rationale**:
    - **Integration**: It is a first-class citizen in NiceGUI.
    - **Performance**: Handles dynamic updates well (adding nodes/edges without full redraw).
    - **Interactivity**: Supports zooming, panning, and dragging nodes out of the box.
- **Alternatives Considered**:
    - **PyVis**: Good for static HTML export, but harder to update incrementally in a real-time web app context.
    - **NetworkX**: Will be used as an intermediate data structure to process the graph before rendering.

### 3. RDF Logging Format: Turtle

- **Decision**: Use **Turtle (.ttl)** format for logs.
- **Rationale**:
    - **Readability**: It is the most human-readable RDF format, which aids debugging.
    - **Append-friendly**: Turtle is reasonably append-friendly (though strictly speaking, prefixes should be at the top, we can manage this by repeating prefixes or using a streaming writer approach if needed, or just parsing the whole file for the GUI).
    - **Standard**: Supported by `rdflib`.

## Implementation Strategy

### Real-time Log Visualization

1.  **Writer (Framework)**: Appends triples to a `.ttl` file.
2.  **Reader (GUI)**:
    -   `ui.timer` triggers every X seconds.
    -   Parses the `.ttl` file using `rdflib`.
    -   Converts RDF triples to a `NetworkX` graph (or directly to ECharts node/link format).
    -   Updates the `ui.echart` element's `options` dictionary.
    -   NiceGUI pushes the diff to the browser.

### RDF Ontology

We need a simple ontology to represent the C-S concepts:
-   `cs:Concept` (Class)
-   `cs:Synchronization` (Class)
-   `cs:Action` (Class)
-   `cs:triggeredBy` (Property)
-   `cs:updatesState` (Property)
