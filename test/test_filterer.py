import json

import pytest
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, XSD

from t2smetrics.core.filterer import (
    T2S,
    Comparison,
    evaluate_rule,
    export_labelstudio_annotations,
    export_wadm_annotations,
    parse_rule,
)


def test_rule_precedence_and_parentheses():
    ast = parse_rule("a[1] || b[1] && c[0]")
    assert evaluate_rule(ast, {"a": 0, "b": 1, "c": 0}) is True
    assert (
        evaluate_rule(parse_rule("(a[1] || b[1]) && c[0]"), {"a": 1, "b": 0, "c": 1})
        is False
    )


@pytest.mark.parametrize(
    "rule,value,expected",
    [
        ("m[0,1]", 0, True),
        ("m]0,1]", 0, False),
        ("m[0,1[", 1, False),
        ("m]0,1[", 1, False),
        ("m[1]", 1, True),
    ],
)
def test_range_boundaries(rule, value, expected):
    assert evaluate_rule(parse_rule(rule), {"m": value}) is expected


def test_missing_metric_is_rejected():
    assert evaluate_rule(parse_rule("missing[1]"), {}) is False


def test_parser_returns_comparison():
    assert parse_rule("metric]0, 0.5]") == Comparison("metric", 0, 0.5, False, True)


def test_wadm_export_encodes_custom_rule_expression(tmp_path):
    path = export_wadm_annotations(
        [
            {
                "annotation_uri": URIRef("urn:test:annotation"),
                "dataset": "example",
                "system": "test-system",
                "case_id": "1",
                "question": "What is the answer?",
                "golden_query": "SELECT * WHERE { ?s ?p ?o }",
                "generated_query": "SELECT * WHERE { ?s ?p ?o }",
                "golden_response": None,
                "generated_response": None,
                "metrics": {"metric_a": 0.5, "metric_b": 1.0},
                "rule": "metric_a]0,0.5] || metric_b[1]",
            }
        ],
        str(tmp_path),
        "example",
    )

    graph = Graph().parse(path, format="turtle")
    error_uri = next(graph.subjects(RDF.type, T2S.ProfilingError))
    rule_uri = graph.value(error_uri, T2S.usedRule)
    assert (rule_uri, RDF.type, T2S.OrExpression) in graph
    assert len(list(graph.objects(rule_uri, T2S.hasMember))) == 2

    comparison_uris = list(graph.subjects(RDF.type, T2S.Comparison))
    assert len(comparison_uris) == 2
    assert all(graph.value(uri, T2S.hasMetric) is not None for uri in comparison_uris)
    assert all(
        graph.value(uri, T2S.minBound).datatype == XSD.decimal
        for uri in comparison_uris
    )
    assert all(
        graph.value(uri, T2S.maxInclusive) is not None for uri in comparison_uris
    )
    assert str(graph.value(rule_uri, T2S.ruleText)) == "metric_a]0,0.5] || metric_b[1]"


def test_wadm_export_writes_annotation_collection(tmp_path):
    path = export_wadm_annotations(
        [
            {
                "annotation_uri": URIRef("urn:test:annotation"),
                "dataset": "example",
                "system": "test-system",
                "case_id": "1",
                "question": "What is the answer?",
                "golden_query": "SELECT * WHERE { ?s ?p ?o }",
                "generated_query": "SELECT * WHERE { ?s ?p ?o }",
                "golden_response": None,
                "generated_response": None,
                "metrics": {"metric_a": 0.5},
                "rule": "metric_a[0,1]",
            }
        ],
        str(tmp_path),
        "example",
    )
    graph = Graph().parse(path, format="turtle")
    dataset_uri = URIRef("urn:t2s:dataset:example")

    assert path.endswith(".ttl")
    assert (dataset_uri, RDF.type, T2S.Dataset) in graph
    assert (URIRef("urn:test:annotation"), RDF.type, T2S.Annotation) in graph
    assert len(list(graph.objects(dataset_uri, T2S.hasCase))) == 1


def test_labelstudio_export_writes_json(tmp_path):
    source = tmp_path / "filter-example.jsonld"
    source.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "target": {
                            "id": "urn:t2s:query:ck25:ck25:47-en",
                            "question": "What is the answer?",
                            "golden_sparql": "SELECT * WHERE { ?s ?p ?o }",
                            "generated_sparql": "SELECT * WHERE { ?s ?p ?o }",
                            "golden_answerset": {
                                "head": {"vars": ["x"]},
                                "results": {"bindings": [{"x": {"value": "a"}}]},
                            },
                            "generated_answerset": {
                                "head": {"vars": ["x"]},
                                "results": {"bindings": [{"x": {"value": "a"}}]},
                            },
                        },
                        "body": {"metrics": {"m": 1.0}},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    path = export_labelstudio_annotations(
        str(source),
        str(tmp_path / "converted"),
        "example",
    )
    assert path.endswith(".json")
    payload = json.loads(pathlib_read(path))
    assert len(payload) == 1
    assert payload[0]["data"]["question_id"] == "urn:t2s:query:ck25:ck25:47-en"
    assert payload[0]["data"]["metrics"]["m"] == 1.0


def pathlib_read(path):
    with open(path, encoding="utf-8") as file:
        return file.read()
