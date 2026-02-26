import yaml
from pathlib import Path

from t2smetrics.core.experiment import Experiment
from t2smetrics.core.dataset import JsonlDataset
from t2smetrics.core.result import EvaluationResult
from t2smetrics.execution.rdflib_backend import RDFLibBackend
from t2smetrics.measures.answer_set.f1_spinach import F1Spinach
from t2smetrics.measures.base import Measure

from t2smetrics.measures.answer_set.f1 import AnswerSetF1
from t2smetrics.measures.answer_set.f1_qald import F1QALD
from t2smetrics.measures.answer_set.hit_at_k import HitAtK
from t2smetrics.measures.answer_set.mrr import MRR
from t2smetrics.measures.answer_set.ndcg import NDCG
from t2smetrics.measures.answer_set.p_at_k import PrecisionAtK
from t2smetrics.measures.answer_set.precision import AnswerSetPrecision
from t2smetrics.measures.answer_set.precision_qald import PrecisionQALD
from t2smetrics.measures.answer_set.recall import AnswerSetRecall
from t2smetrics.measures.answer_set.recall_qald import RecallQALD
from t2smetrics.measures.codebleu.codebleu import CodeBLEU
from t2smetrics.measures.distance import (
    CosineSimilarity,
    EuclideanDistance,
    JaccardSimilarity,
    LevenshteinDistance,
)
from t2smetrics.measures.exact import QueryExactMatch
from t2smetrics.measures.query_execution import QueryExecution
from t2smetrics.measures.text_metrics import Bleu, Meteor, RougeN
from t2smetrics.measures.token import TokenF1, TokenPrecision, TokenRecall
from t2smetrics.measures.uri.uri_hallucination import URIHallucination

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


def str_to_measure(measure_name: str) -> Measure:

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
        # "URIHallucination": URIHallucination(),
        "Bleu": Bleu(),
        # "Meteor": Meteor(),
        # "RougeN": RougeN(n=2),
        # "TokenPrecision": TokenPrecision(),
        # "TokenRecall": TokenRecall(),
        # "TokenF1": TokenF1(),
        # "CodeBLEU": CodeBLEU(),
    }

    if measure_name not in mapping:
        raise ValueError(f"Unknown measure name: {measure_name}")

    return mapping[measure_name]


def run_single_case(
    file_cases_id: str, case_id: str, measures: set[Measure] = None
) -> EvaluationResult:

    graph_path = DATA_DIR / "graphs" / f"{file_cases_id}.ttl"
    backend = RDFLibBackend(str(graph_path))

    dataset = JsonlDataset(DATA_DIR / "cases" / f"{file_cases_id}.jsonl")

    # Filter dataset to only include the specific case_id
    dataset = [x for x in dataset if x.id == case_id]

    if not dataset:
        raise ValueError(f"No data found for case_id: {case_id}")

    experiment = Experiment(
        dataset=dataset,
        measures=measures,
        execution_backend=backend,
        verbose=False,
    )

    results, _ = experiment.run()

    return results[0]
