from cs_framework.engine.runner import Runner
from cs_framework.core.concept import Concept

class TestConcept(Concept):
    def __init__(self, name: str):
        super().__init__(name)
        self._state = {"value": 0}

    def add(self, payload: dict):
        self._state["value"] += payload.get("amount", 1)

runner = Runner()
c = TestConcept("TestConcept")
runner.register(c)
runner.start()
