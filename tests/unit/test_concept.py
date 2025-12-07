import pytest
from cs_framework.core.concept import Concept

class TestConcept(Concept):
    def __init__(self, name="Test"):
        super().__init__(name)
        self._state = {"count": 0}

    def increment(self, payload):
        self._state["count"] += payload.get("amount", 1)
        self.emit("Incremented", {"new_count": self._state["count"]})

def test_concept_initialization():
    c = TestConcept()
    assert c.name == "Test"
    assert c._state["count"] == 0

def test_concept_dispatch():
    c = TestConcept()
    c.dispatch("increment", {"amount": 5})
    assert c._state["count"] == 5

def test_concept_events():
    c = TestConcept()
    c.dispatch("increment", {"amount": 1})
    events = c.collect_events()
    assert len(events) == 1
    assert events[0].name == "Incremented"
    assert events[0].payload["new_count"] == 1
    assert events[0].source_id == c.id

def test_concept_invalid_action():
    c = TestConcept()
    with pytest.raises(AttributeError):
        c.dispatch("non_existent", {})

def test_state_snapshot_immutability():
    c = TestConcept()
    snapshot = c.get_state_snapshot()
    snapshot["count"] = 999
    assert c._state["count"] == 0
