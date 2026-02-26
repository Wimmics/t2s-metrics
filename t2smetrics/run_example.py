from t2smetrics.core.experiment import Experiment
from t2smetrics.core.dataset import JsonlDataset
from t2smetrics.execution.rdflib_backend import RDFLibBackend

from t2smetrics.llm.ollama_backend import OllamaBackend
from t2smetrics.measures.answer_set.f1 import AnswerSetF1
from t2smetrics.measures.answer_set.precision import AnswerSetPrecision
from t2smetrics.measures.answer_set.precision_qald import PrecisionQALD
from t2smetrics.measures.answer_set.recall import AnswerSetRecall
from t2smetrics.measures.answer_set.recall_qald import RecallQALD
from t2smetrics.measures.exact import QueryExactMatch
from t2smetrics.measures.codebleu.codebleu import CodeBLEU
from t2smetrics.measures.answer_set.f1_qald import F1QALD
from t2smetrics.measures.answer_set.f1_spinach import F1Spinach
from t2smetrics.measures.answer_set.mrr import MRR
from t2smetrics.measures.answer_set.hit_at_k import HitAtK
from t2smetrics.measures.answer_set.ndcg import NDCG
from t2smetrics.measures.answer_set.p_at_k import PrecisionAtK
from t2smetrics.measures.distance import (
    LevenshteinDistance,
    JaccardSimilarity,
    CosineSimilarity,
    EuclideanDistance,
)
from t2smetrics.measures.llm_judge import LLMJudge
from t2smetrics.measures.text_metrics import Bleu, RougeN, Meteor, SPBleu
from t2smetrics.measures.uri.uri_hallucination import URIHallucination
from t2smetrics.measures.query_execution import QueryExecution
from t2smetrics.measures.token import SPF1, TokenRecall, TokenPrecision, TokenF1


dataset = JsonlDataset("./example_dataset.jsonl")

execution_backend = RDFLibBackend("example.ttl")

llm_backend = OllamaBackend()

measures = [
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
    dataset=dataset,
    measures=measures,
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
