from pathlib import Path

import yaml

from t2smetrics.core.eval import JsonlEval
from t2smetrics.core.experiment import Experiment
from t2smetrics.core.result import EvaluationResult
from t2smetrics.execution.rdflib_backend import RDFLibBackend
from t2smetrics.metrics.answer_set.f1_spinach import F1Spinach
from t2smetrics.metrics.answer_set.precision import AnswerSetPrecision
from t2smetrics.metrics.base import Metric
from t2smetrics.metrics.text_metrics import Bleu, SPBleu
from t2smetrics.metrics.token import SPF1
from t2smetrics.metrics.uri.uri_hallucination import URIHallucination

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


def str_to_metric(metric_name: str) -> Metric:

    mapping = {
        "AnswerSetPrecision": AnswerSetPrecision(),
        # "AnswerSetRecall": AnswerSetRecall(),
        # "AnswerSetF1": AnswerSetF1(),
        # "PrecisionQALD": PrecisionQALD(),
        # "RecallQALD": RecallQALD(),
        # "F1QALD": F1QALD(),
        "F1Spinach": F1Spinach(),
        # "HitAtK": HitAtK(k=5),
        # "MRR": MRR(),
        # "NDCG": NDCG(k=5),
        # "PrecisionAtK": PrecisionAtK(k=5),
        # "QueryExactMatch": QueryExactMatch(),
        # "CosineSimilarity": CosineSimilarity(),
        # "EuclideanDistance": EuclideanDistance(),
        # "JaccardSimilarity": JaccardSimilarity(),
        # "LevenshteinDistance": LevenshteinDistance(),
        "URIHallucination": URIHallucination(),
        "Bleu": Bleu(),
        "SP-Bleu": SPBleu(),
        "SP-F1": SPF1(),
        # "Meteor": Meteor(),
        # "RougeN": RougeN(n=2),
        # "TokenPrecision": TokenPrecision(),
        # "TokenRecall": TokenRecall(),
        # "TokenF1": TokenF1(),
        # "CodeBLEU": CodeBLEU(),
    }

    if metric_name not in mapping:
        raise ValueError(f"Unknown metric name: {metric_name}")

    return mapping[metric_name]


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
