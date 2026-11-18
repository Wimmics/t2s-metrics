import json

import pytest

from t2smetrics.core.context import EvaluationContext
from t2smetrics.core.engine import EvaluationEngine
from t2smetrics.core.eval import JsonlEval
from t2smetrics.core.export import (
    check_coherence_of_results,
    export_experiment_runs,
    export_experiment_runs_turtle,
)
from t2smetrics.core.result import EvaluationResult


class Metric:
    name = "test"
    requires_execution = False
    requires_llm = False

    def run(self, case, context):
        return EvaluationResult(case.id, self.name, 1)


def test_engine_enforces_requirements_and_evaluates_cases():
    case = next(iter([type("Case", (), {"id": "1", "order_matters": True})()]))
    engine = EvaluationEngine([Metric()], EvaluationContext())
    assert engine.evaluate_case(case) == {EvaluationResult("1", "test", 1)}
    assert len(engine.evaluate([case])) == 1

    required = Metric()
    required.name = "execution"
    required.requires_execution = True
    with pytest.raises(RuntimeError):
        EvaluationEngine([required], EvaluationContext()).evaluate_case(case)

    required.requires_execution = False
    required.requires_llm = True
    with pytest.raises(RuntimeError):
        EvaluationEngine([required], EvaluationContext()).evaluate_case(case)


def test_jsonl_eval_reports_invalid_rows(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text('{"id": "missing"}\n')
    with pytest.raises(ValueError, match="Error parsing JSON line"):
        list(JsonlEval(str(path)))


def test_export_coherence_and_json_export(tmp_path):
    class Run:
        dataset = "d"
        system_name = "s"
        summary = {"f1": 1.0}
        results = [EvaluationResult("1", "f1", 1.0)]
        cases = []

    run = Run()
    with pytest.raises(ValueError):
        check_coherence_of_results([])
    run.summary = None
    with pytest.raises(ValueError):
        check_coherence_of_results([run])
    run.summary = {"f1": 1.0}
    export_experiment_runs([run], str(tmp_path), per_query=True)
    output = next(tmp_path.glob("*.json"))
    assert json.loads(output.read_text())[0]["per_query_results"][0]["score"] == 1.0
    with pytest.raises(ValueError):
        export_experiment_runs([run], str(tmp_path), export_format="xml")


def test_export_turtle_contains_dataset_system_and_endpoint(tmp_path):
    class Run:
        dataset = "d"
        system_name = "s"
        summary = {"f1 score": 1.0}
        results = []
        cases = []

    output = export_experiment_runs_turtle([Run()], str(tmp_path), "http://endpoint")
    assert "Dataset" in output and "System" in output and "f1_score" in output
