from t2smetrics.core.experiment import Experiment
from t2smetrics.core.eval import JsonlEval
from t2smetrics.execution.rdflib_backend import RDFLibBackend

from t2smetrics.llm.ollama_backend import OllamaBackend
from t2smetrics.metrics.answer_set.f1 import AnswerSetF1
from t2smetrics.metrics.answer_set.precision import AnswerSetPrecision
from t2smetrics.metrics.answer_set.precision_qald import PrecisionQALD
from t2smetrics.metrics.answer_set.recall import AnswerSetRecall
from t2smetrics.metrics.answer_set.recall_qald import RecallQALD
from t2smetrics.metrics.exact import QueryExactMatch
from t2smetrics.metrics.codebleu.codebleu import CodeBLEU
from t2smetrics.metrics.answer_set.f1_qald import F1QALD
from t2smetrics.metrics.answer_set.f1_spinach import F1Spinach
from t2smetrics.metrics.answer_set.mrr import MRR
from t2smetrics.metrics.answer_set.hit_at_k import HitAtK
from t2smetrics.metrics.answer_set.ndcg import NDCG
from t2smetrics.metrics.answer_set.p_at_k import PrecisionAtK
from t2smetrics.metrics.distance import (
    LevenshteinDistance,
    JaccardSimilarity,
    CosineSimilarity,
    EuclideanDistance,
)
from t2smetrics.metrics.llm_judge import LLMJudge
from t2smetrics.metrics.text_metrics import Bleu, RougeN, Meteor, SPBleu
from t2smetrics.metrics.uri.uri_hallucination import URIHallucination
from t2smetrics.metrics.query_execution import QueryExecution
from t2smetrics.metrics.token import SPF1, TokenRecall, TokenPrecision, TokenF1


jsonl_eval = JsonlEval("./datasets/example/eval/example.jsonl")

execution_backend = RDFLibBackend("./datasets/example/kg/example.ttl")

llm_backend = OllamaBackend()

metrics = [
    AnswerSetPrecision(),
    AnswerSetRecall(),
    AnswerSetF1(),
    Bleu(),
    SPBleu(),
    CodeBLEU(),
    CosineSimilarity(),
    EuclideanDistance(),
    F1QALD(),
    PrecisionQALD(),
    RecallQALD(),
    F1Spinach(),
    HitAtK(k=5),
    JaccardSimilarity(),
    LLMJudge(),
    LevenshteinDistance(),
    MRR(),
    Meteor(),
    NDCG(),
    PrecisionAtK(k=1),
    QueryExecution(),
    QueryExactMatch(),
    RougeN(1),
    RougeN(2),
    RougeN(3),
    RougeN(4),
    TokenF1(),
    SPF1(),
    TokenPrecision(),
    TokenRecall(),
    URIHallucination(),
]

experiment = Experiment(
    jsonl_eval=jsonl_eval,
    metrics=metrics,
    execution_backend=execution_backend,
    llm_backend=llm_backend,
    verbose=True,
)

results, summary = experiment.run()

print("=== PER QUERY RESULTS ===")
for r in results:
    print(r)

print("\n=== SUMMARY ===")
for k, v in summary.items():
    print(f"{k}: {v:.4f}")
