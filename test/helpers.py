from pathlib import Path

import yaml

from t2smetrics.core.eval import JsonlEval
from t2smetrics.core.experiment import Experiment
from t2smetrics.core.result import EvaluationResult
from t2smetrics.execution.rdflib_backend import RDFLibBackend
from t2smetrics.metrics.base import Metric

DATA_DIR = Path(__file__).parent / "data"


def check_available_file_cases():
    path = DATA_DIR / "cases"
    cases = []
    for file in path.glob("*.jsonl"):
        cases.append(file.stem)
    return cases


def load_expectations(filename):
    path = DATA_DIR / "expectations" / filename
    with open(path) as f:
        return yaml.safe_load(f)


def run_single_case(
    file_cases_id: str, case_id: str, metrics: set[Metric] = None
) -> EvaluationResult:

    graph_path = DATA_DIR / "graphs" / f"{file_cases_id}.ttl"
    backend = RDFLibBackend(str(graph_path))

    jsonl_eval = JsonlEval(DATA_DIR / "cases" / f"{file_cases_id}.jsonl")

    # Filter jsonl_eval to only include the specific case_id
    jsonl_eval = [x for x in jsonl_eval if x.id == case_id]

    if not jsonl_eval:
        raise ValueError(f"No data found for case_id: {case_id}")

    experiment = Experiment(
        jsonl_eval=jsonl_eval,
        metrics=metrics,
        execution_backend=backend,
        verbose=False,
    )

    results, _ = experiment.run()

    return results.pop()
