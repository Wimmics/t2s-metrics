from t2smetrics.core.eval import JsonlEval
from t2smetrics.core.experiment import Experiment
from t2smetrics.execution.rdflib_backend import RDFLibBackend
from t2smetrics.llm.ollama_backend import OllamaBackend
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
    LLMJudge,
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
