import json

import pytest

from t2smetrics.core.linter import (
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


def test_wadm_export_writes_annotation_collection(tmp_path):
    path = export_wadm_annotations(
        [{"type": "Annotation", "motivation": "assessing"}],
        str(tmp_path),
        "example",
    )
    document = json.loads(pathlib_read(path))
    assert document["type"] == "AnnotationCollection"
    assert len(document["items"]) == 1
    assert "http://www.w3.org/ns/anno.jsonld" in document["@context"]


def test_labelstudio_export_writes_json(tmp_path):
    source = tmp_path / "lint-example.jsonld"
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
