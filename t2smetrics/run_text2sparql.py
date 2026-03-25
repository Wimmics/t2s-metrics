import logging

from t2smetrics import run_experiments
from t2smetrics.core.logging import setup_third_party_logging
from t2smetrics.metrics import (
    F1QALD,
    MRR,
    NDCG,
    SPF1,
    AnswerSetF1,
    AnswerSetPrecision,
    AnswerSetRecall,
    Bleu,
    CodeBLEU,
    CosineSimilarity,
    EuclideanDistance,
    F1Spinach,
    HitAtK,
    JaccardSimilarity,
    LevenshteinDistance,
    Meteor,
    PrecisionAtK,
    PrecisionQALD,
    QueryExactMatch,
    QueryExecution,
    RecallQALD,
    RougeN,
    SPBleu,
    TokenF1,
    TokenPrecision,
    TokenRecall,
    URIHallucination,
)

setup_third_party_logging(logging.WARNING)

dataset_name = "ck25"
question_answering_systems = [
    "AIFB",
    "DBPEDIA-CG",
    "DBPEDIA-CL",
    "DBPEDIA-SC",
    "FRANZ",
    "IIS-L",
    "IIS-Q",
    "INFAI",
    "LABIC",
    "LACODAM",
    "MIPT",
    "WSE",
]
endpoint_url = "http://localhost:8886/"
jsonl_paths = [
    f"./datasets/{dataset_name}/eval/{qa}.jsonl" for qa in question_answering_systems
]
metrics = [
    AnswerSetPrecision(),
    AnswerSetRecall(),
    AnswerSetF1(),
    Bleu(),
    CodeBLEU(),
    CosineSimilarity(),
    EuclideanDistance(),
    F1QALD(),
    SPBleu(),
    SPF1(),
    HitAtK(k=1),
    JaccardSimilarity(),
    LevenshteinDistance(),
    MRR(),
    Meteor(),
    NDCG(),
    PrecisionAtK(k=1),
    PrecisionQALD(),
    QueryExecution(),
    QueryExactMatch(),
    RecallQALD(),
    RougeN(4),
    TokenF1(),
    TokenPrecision(),
    TokenRecall(),
    URIHallucination(),
    F1Spinach(),
]

run_experiments.run(
    dataset=dataset_name,
    systems_name=question_answering_systems,
    jsonl_evals=jsonl_paths,
    metrics_list=metrics,
    execution_backend_endpoint_url=endpoint_url,
    per_query=False,
    parallel=True,
    verbose=True,
)
