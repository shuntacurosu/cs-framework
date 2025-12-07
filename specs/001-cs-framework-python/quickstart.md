# Quickstart: C-S Framework for Python

## Installation

```bash
pip install cs-framework
```

## 1. Define Concepts

Create independent concepts by inheriting from `Concept`. Ensure state is managed privately and exposed via `get_state_snapshot`.

```python
from cs_framework.core import Concept

class User(Concept):
    def __init__(self, name="User"):
        super().__init__(name)
        self._state = {"is_logged_in": False, "username": None}

    def login(self, username):
        # Action logic
        self._state["is_logged_in"] = True
        self._state["username"] = username
        # Emit event
        self.emit("LoggedIn", {"username": username})

    def get_state_snapshot(self):
        # Return immutable copy
        return self._state.copy()
```

## 2. Define Synchronizations

Link concepts using the `Synchronization` class with the "When-Where-Then" pattern.

```python
from cs_framework.core import Synchronization, EventPattern, ActionInvocation

# Define the rule:
# WHEN: User emits "LoggedIn"
# WHERE: User is actually active (example condition)
# THEN: Trigger "LogAccess" on AuditLog AND "Increment" on Metrics

sync = Synchronization(
    name="LogAccessOnLogin",
    when=EventPattern(source=user_concept, event_name="LoggedIn"),
    where=lambda state: state[user_concept.id]["is_logged_in"] is True,
    then=[
        ActionInvocation(
            target=audit_concept, 
            action_name="LogAccess",
            payload_mapper=lambda event: {"user": event.payload["username"]}
        ),
        ActionInvocation(
            target=metrics_concept,
            action_name="IncrementCounter",
            payload_mapper=lambda event: {"metric": "login_count"}
        )
    ]
)
```

## 3. Run the Application

```python
from cs_framework.engine import Runner

runner = Runner()
runner.register(user_concept)
runner.register(audit_concept)
runner.register(metrics_concept)
runner.register(sync)

# This will generate 'execution.ttl' log file
runner.start()

# Trigger action
user_concept.dispatch("login", "alice")
```

## 4. Visualize Execution

Run the GUI tool to see the execution graph in real-time.

```bash
csfw gui --log execution.ttl
```

Open your browser at `http://localhost:8080`.
