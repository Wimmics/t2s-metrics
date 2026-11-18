from unittest.mock import Mock

import pytest

from t2smetrics.execution.rdflib_backend import RDFLibBackend
from t2smetrics.execution.result_utils import normalize_query_response
from t2smetrics.execution.sparql_endpoint_backend import SparqlEndpointBackend


def test_rdflib_backend_executes_query_and_returns_json(tmp_path):
    graph = tmp_path / "graph.ttl"
    graph.write_text("@prefix ex: <http://example.org/> . ex:a ex:p ex:b .")
    backend = RDFLibBackend(str(graph), safe_limit=1)
    response = backend.execute("SELECT ?o WHERE { <http://example.org/a> <http://example.org/p> ?o }")
    assert normalize_query_response(response) == [("http://example.org/b",)]


def test_rdflib_backend_reports_parse_and_query_errors(tmp_path):
    with pytest.raises(ValueError):
        RDFLibBackend(str(tmp_path / "missing.ttl"))

    graph = tmp_path / "graph.ttl"
    graph.write_text("@prefix ex: <http://example.org/> . ex:a ex:p ex:b .")
    assert RDFLibBackend(str(graph)).execute("not valid sparql") is None


def test_endpoint_backend_configures_wrapper_and_handles_errors(monkeypatch):
    wrapper = Mock()
    wrapper.query.return_value.convert.return_value = {"boolean": True}
    monkeypatch.setattr(
        "t2smetrics.execution.sparql_endpoint_backend.SPARQLWrapper",
        lambda url: wrapper,
    )
    backend = SparqlEndpointBackend("", safe_limit=1)
    with pytest.raises(ValueError):
        backend.execute("SELECT * {}")

    backend = SparqlEndpointBackend.__new__(SparqlEndpointBackend)
    backend.endpoint_url = "http://example.test/sparql"
    backend.timeout = 3
    backend.default_graph = "http://example.test/graph"
    backend.headers = {"X-Test": "yes"}
    backend.safe_limit = 0
    assert backend.execute("ASK {}") == {"boolean": True}
    wrapper.setReturnFormat.assert_called_once()
    wrapper.addDefaultGraph.assert_called_once_with(backend.default_graph)
    wrapper.addCustomHttpHeader.assert_called_once_with("X-Test", "yes")

    wrapper.query.side_effect = RuntimeError("offline")
    assert backend.execute("ASK {}") is None
