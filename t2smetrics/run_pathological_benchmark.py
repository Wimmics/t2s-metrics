import json
import pandas as pd
from tqdm import tqdm

from t2smetrics.core.dataset import JsonlDataset
from t2smetrics.core.experiment import Experiment
from t2smetrics.execution.rdflib_backend import RDFLibBackend
from t2smetrics.llm.ollama_backend import OllamaBackend
from t2smetrics.measures.answer_set.f1 import AnswerSetF1
from t2smetrics.measures.answer_set.f1_qald import F1QALD
from t2smetrics.measures.answer_set.f1_spinach import F1Spinach
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
from t2smetrics.measures.llm_judge import LLMJudge
from t2smetrics.measures.query_execution import QueryExecution
from t2smetrics.measures.text_metrics import Bleu, Meteor, QCanBleu, RougeN, SPBleu
from t2smetrics.measures.token import SPF1, TokenF1, TokenPrecision, TokenRecall
from t2smetrics.measures.uri.uri_hallucination import URIHallucination

dataset = JsonlDataset("./res/pb-q2set/pb_q2set.jsonl")

execution_backend = RDFLibBackend("./res/pb-q2set/dataset.ttl")

llm_backend = OllamaBackend()

# Instantiate metrics
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
    QCanBleu(),
    TokenPrecision(),
    TokenRecall(),
    URIHallucination(),
]

experiment = Experiment(
    dataset=dataset,
    measures=metrics,
    execution_backend=execution_backend,
    llm_backend=llm_backend,
    verbose=True,
)

results, summary = experiment.run()


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f]


rows = []

for example in tqdm(load_jsonl("./res/pb-q2set/pb_q2set.jsonl")):
    result_row = {
        "id": example["id"],
        "expected_score": example["expected_score"],
    }

    for result in results:
        if result.id == example["id"]:
            result_row[result.measure] = result.score

    rows.append(result_row)

df = pd.DataFrame(rows)

df.to_csv("./res/pb-q2set/benchmark_results.csv", index=False)
# print("Saved results to benchmark_results.csv")
# df.to_html("./res/pb-q2set/benchmark_results.html", index=False)
# print(df.head())
