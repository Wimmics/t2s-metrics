import json
import logging
import os
import time
import warnings

from t2smetrics.core.eval import JsonlEval
from t2smetrics.core.experiment import Experiment
from t2smetrics.execution.sparql_endpoint_backend import SparqlEndpointBackend
from t2smetrics.llm.ollama_backend import OllamaBackend
from t2smetrics.metrics.answer_set.f1 import AnswerSetF1
from t2smetrics.metrics.answer_set.f1_qald import F1QALD
from t2smetrics.metrics.answer_set.f1_spinach import F1Spinach
from t2smetrics.metrics.answer_set.hit_at_k import HitAtK
from t2smetrics.metrics.answer_set.mrr import MRR
from t2smetrics.metrics.answer_set.ndcg import NDCG
from t2smetrics.metrics.answer_set.p_at_k import PrecisionAtK
from t2smetrics.metrics.answer_set.precision import AnswerSetPrecision
from t2smetrics.metrics.answer_set.precision_qald import PrecisionQALD
from t2smetrics.metrics.answer_set.recall import AnswerSetRecall
from t2smetrics.metrics.answer_set.recall_qald import RecallQALD
from t2smetrics.metrics.codebleu.codebleu import CodeBLEU
from t2smetrics.metrics.distance import (
    CosineSimilarity,
    EuclideanDistance,
    JaccardSimilarity,
    LevenshteinDistance,
)
from t2smetrics.metrics.exact import QueryExactMatch
from t2smetrics.metrics.query_execution import QueryExecution
from t2smetrics.metrics.text_metrics import Bleu, Meteor, RougeN, SPBleu
from t2smetrics.metrics.token import SPF1, TokenF1, TokenPrecision, TokenRecall
from t2smetrics.metrics.uri.uri_hallucination import URIHallucination

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
warnings.filterwarnings("ignore", category=RuntimeWarning, module="SPARQLWrapper")
logging.getLogger("SPARQLWrapper").disabled = True

# Suppress specific loggers likely used by LangGraph / ChatLLaMA
logging.getLogger("langgraph").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)  # if using httpx
logging.getLogger("urllib3").setLevel(logging.WARNING)  # if using requests
logging.getLogger("uvicorn").setLevel(logging.WARNING)  # sometimes used for servers

# Optional: completely silence a specific logger
logging.getLogger("langgraph.server").propagate = False

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

dataset_name = "ck25"
endpoint_url = "http://localhost:8886/"

all_qa_results = []

start_time = time.time()

for qa in question_answering_systems:
    jsonl_eval = JsonlEval(f"./datasets/{dataset_name}/eval/{qa}.jsonl")

    execution_backend = SparqlEndpointBackend(endpoint_url)

    llm_backend = OllamaBackend()

    metrics = [
        AnswerSetPrecision(),
        AnswerSetRecall(),
        AnswerSetF1(),
        Bleu(),
        CodeBLEU(),
        CosineSimilarity(),
        EuclideanDistance(),
        F1QALD(),
        F1Spinach(),
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

    print(f"== SUMMARY {qa} ===")
    for k, v in summary.items():
        print(f"{k}: {v:.4f}")

    all_qa_results.append(
        {"dataset": dataset_name, "system_name": qa, "metrics": summary}
    )

end_time = time.time()
logging.info(f"Execution time: {int(end_time - start_time)} seconds")

current_time = time.strftime("%Y%m%d-%H%M%S")

file_path = f"./datasets/{dataset_name}/results/{dataset_name}-{current_time}.json"
os.makedirs(os.path.dirname(file_path), exist_ok=True)

with open(file_path, "w") as f:
    json.dump(all_qa_results, f, indent=2)
