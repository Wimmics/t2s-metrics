import json

from t2smetrics.core.converter import (
    render_sparql_table,
    transform_jsonld_to_labelstudio,
)


def test_render_sparql_table_handles_empty_boolean_and_missing_bindings():
    assert render_sparql_table({}) == ""
    boolean = render_sparql_table({"boolean": True}, is_golden=True)
    assert "Result" in boolean and "True" in boolean

    table = render_sparql_table(
        {
            "head": {"vars": ["name", "age"]},
            "results": {"bindings": [{"name": {"value": "Ada"}}]},
        }
    )
    assert "<th" in table
    assert "Ada" in table
    assert "age" in table


def test_transform_jsonld_to_labelstudio_preserves_data_and_renders_answers():
    source = {
        "items": [
            {
                "target": {
                    "id": "case-1",
                    "dataset": "example",
                    "system": "baseline",
                    "question": "Who?",
                    "golden_sparql": "ASK {}",
                    "generated_sparql": "ASK {}",
                    "golden_answerset": {"boolean": True},
                    "generated_answerset": {},
                },
                "body": {"metrics": {"f1": 1.0}},
            }
        ]
    }
    result = json.loads(transform_jsonld_to_labelstudio(json.dumps(source)))
    assert result[0]["data"]["question_id"] == "case-1"
    assert result[0]["data"]["metrics"]["f1"] == 1.0
    assert "True" in result[0]["data"]["golden_answerset_html"]
