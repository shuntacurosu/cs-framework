import uuid
import os
import pytest
from rdflib import Graph, RDF
from cs_framework.logging.logger import RDFLogger
from cs_framework.logging.ontology import CONCEPT, ACTION, EVENT, HAS_NAME

def test_logger_concept():
    logger = RDFLogger(console_output=False)
    cid = uuid.uuid4()
    logger.log_concept(cid, "TestConcept", {"key": "value"})
    
    # Check graph
    assert (None, RDF.type, CONCEPT) in logger.graph
    assert (None, HAS_NAME, None) in logger.graph

def test_logger_save():
    filename = "test_log.ttl"
    logger = RDFLogger(log_file=filename, console_output=False)
    cid = uuid.uuid4()
    logger.log_concept(cid, "TestConcept", {})
    logger.save()
    
    assert os.path.exists(filename)
    
    # Load back
    g = Graph()
    g.parse(filename, format="turtle")
    assert len(g) > 0
    
    os.remove(filename)

def test_logger_full_flow():
    logger = RDFLogger(console_output=False)
    cid = uuid.uuid4()
    aid = uuid.uuid4()
    eid = uuid.uuid4()
    
    logger.log_concept(cid, "MyConcept", {})
    logger.log_action(aid, "MyAction", cid)
    logger.log_event(eid, "MyEvent", cid, causal_link=aid)
    
    # Verify triples exist
    # We can query the graph
    q = """
    PREFIX cs: <http://cs-framework.org/schema/>
    SELECT ?name WHERE {
        ?s a cs:Concept .
        ?s cs:hasName ?name .
    }
    """
    results = logger.graph.query(q)
    names = [str(r[0]) for r in results]
    assert "MyConcept" in names
