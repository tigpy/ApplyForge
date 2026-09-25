"""
Tests for Connector Registry and Mock Discovery
"""
from packages.connectors.registry import connector_registry

def test_mock_connector_search():
    connector = connector_registry.get("mock")
    assert connector.health_check() is True
    jobs = connector.search("python")
    assert len(jobs) >= 2
    normalized = connector.normalize(jobs[0])
    assert "title" in normalized
    assert "company" in normalized
