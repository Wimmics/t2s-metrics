import json

import pytest

from t2smetrics.linter import (
    Comparison,
    evaluate_rule,
    export_wadm_annotations,
    parse_rule,
)


def test_rule_precedence_and_parentheses():
    ast = parse_rule("a[1] || b[1] && c[0]")
    assert evaluate_rule(ast, {"a": 0, "b": 1, "c": 0}) is True
    assert evaluate_rule(parse_rule("(a[1] || b[1]) && c[0]"), {"a": 1, "b": 0, "c": 1}) is False


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
    with pytest.raises(ValueError, match="was not computed"):
        evaluate_rule(parse_rule("missing[1]"), {})


def test_parser_returns_comparison():
    assert parse_rule("metric]0, 0.5]") == Comparison(
        "metric", 0, 0.5, False, True
    )


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


def pathlib_read(path):
    with open(path, encoding="utf-8") as file:
        return file.read()