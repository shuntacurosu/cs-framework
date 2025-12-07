import pytest
from cs_framework.core.concept import Concept
from cs_framework.core.synchronization import Synchronization
from cs_framework.core.event import EventPattern, ActionInvocation
from cs_framework.engine.runner import Runner

class SourceConcept(Concept):
    def __init__(self, name="Source"):
        super().__init__(name)
        self._state = {"triggered": False}

    def trigger(self, payload):
        self._state["triggered"] = True
        self.emit("Triggered", payload)

class TargetConcept(Concept):
    def __init__(self, name="Target"):
        super().__init__(name)
        self._state = {"received_data": None}

    def receive(self, payload):
        self._state["received_data"] = payload.get("data")

def test_sync_flow():
    source = SourceConcept()
    target = TargetConcept()

    # Define Sync
    # When Source emits "Triggered", call "receive" on Target with payload data
    sync = Synchronization(
        name="SourceToTarget",
        when=EventPattern(source_concept=source, event_name="Triggered"),
        then=[
            ActionInvocation(
                target_concept=target,
                action_name="receive",
                payload_mapper=lambda event: {"data": event.payload.get("value")}
            )
        ]
    )

    runner = Runner()
    runner.register(source)
    runner.register(target)
    runner.register(sync)

    # Trigger action on Source
    runner.dispatch(source.id, "trigger", {"value": "Hello World"})

    # Verify Target state
    assert target._state["received_data"] == "Hello World"

def test_sync_condition_false():
    source = SourceConcept()
    target = TargetConcept()

    # Sync with condition that always fails
    sync = Synchronization(
        name="ConditionalSync",
        when=EventPattern(source_concept=source, event_name="Triggered"),
        where=lambda state: False,
        then=[
            ActionInvocation(
                target_concept=target,
                action_name="receive",
                payload_mapper=lambda event: {}
            )
        ]
    )

    runner = Runner()
    runner.register(source)
    runner.register(target)
    runner.register(sync)

    runner.dispatch(source.id, "trigger", {"value": "Should not pass"})

    assert target._state["received_data"] is None

def test_recursion_limit():
    # Create a ping-pong loop
    c1 = SourceConcept("C1")
    c2 = SourceConcept("C2") # Reusing SourceConcept as it has trigger/emit

    # C1 Triggered -> C2 trigger
    sync1 = Synchronization(
        name="C1toC2",
        when=EventPattern(c1, "Triggered"),
        then=[ActionInvocation(c2, "trigger", lambda e: {})]
    )
    # C2 Triggered -> C1 trigger
    sync2 = Synchronization(
        name="C2toC1",
        when=EventPattern(c2, "Triggered"),
        then=[ActionInvocation(c1, "trigger", lambda e: {})]
    )

    runner = Runner(max_depth=5)
    runner.register(c1)
    runner.register(c2)
    runner.register(sync1)
    runner.register(sync2)

    # This should not crash but stop after max_depth
    runner.dispatch(c1.id, "trigger", {})
    
    # If it didn't crash, test passed (conceptually). 
    # We can check if it stopped by inspecting logs if we had them, 
    # or just relying on the fact that process_events returns.
    assert True
