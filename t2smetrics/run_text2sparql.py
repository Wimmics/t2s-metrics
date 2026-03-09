import json
import time
from t2smetrics.core.experiment import Experiment
from t2smetrics.core.dataset import JsonlDataset
from t2smetrics.execution.sparql_endpoint_backend import SparqlEndpointBackend
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
from t2smetrics.measures.text_metrics import Bleu, QCanBleu, RougeN, Meteor, SPBleu
from t2smetrics.measures.uri.uri_hallucination import URIHallucination
from t2smetrics.measures.query_execution import QueryExecution
from t2smetrics.measures.token import SPF1, TokenRecall, TokenPrecision, TokenF1
import logging
import warnings

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
    # "Testing",
]

# dataset_name = "db25"
# endpoint_url = "http://localhost:8887/"

dataset_name = "ck25"
endpoint_url = "http://localhost:8888/"

all_qa_results = []

start_time = time.time()

for qa in question_answering_systems:

    dataset = JsonlDataset(f"./res/{dataset_name}/{qa}.jsonl")

    execution_backend = SparqlEndpointBackend(endpoint_url)
    llm_backend = OllamaBackend()

    measures = [
        AnswerSetPrecision(),  # OK
        AnswerSetRecall(),  # OK
        AnswerSetF1(),  # OK
        Bleu(),  # OK
        CodeBLEU(),  # OK
        # CosineSimilarity(),  # OK
        # EuclideanDistance(),  # OK
        # F1QALD(),  # OK
        # F1Spinach(),  # OK
        # SPBleu(),  # OK
        # SPF1(),  # OK
        # HitAtK(k=1),  # OK
        # JaccardSimilarity(),  # OK
        # # LLMJudge(),  # OK
        # LevenshteinDistance(),  # OK
        # MRR(),  # OK
        # Meteor(),  # OK
        # NDCG(),  # OK
        # PrecisionAtK(k=1),  # OK
        # PrecisionQALD(),  # OK
        # QCanBleu(),  # OK
        # QueryExecution(),  # OK
        # QueryExactMatch(),  # OK
        # RecallQALD(),  # OK
        # RougeN(4),  # OK
        # TokenF1(),  # OK
        # TokenPrecision(),  # OK
        # TokenRecall(),  # OK
        # URIHallucination(),  # OK
    ]

    experiment = Experiment(
        dataset=dataset,
        measures=measures,
        execution_backend=execution_backend,
        llm_backend=llm_backend,
        verbose=True,
        # cache_result_sets=False
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
with open(f"./res/results/{dataset_name}-{current_time}.json", "w") as f:
    json.dump(all_qa_results, f, indent=2)
