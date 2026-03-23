import logging
import time
import warnings

from t2smetrics.core.eval import JsonlEval
from t2smetrics.core.experiment import Experiment
from t2smetrics.core.export import export_experiment_runs
from t2smetrics.execution.sparql_endpoint_backend import SparqlEndpointBackend
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

experiment_runs = []

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
        dataset=dataset_name,
        system_name=qa,
        jsonl_eval=jsonl_eval,
        metrics=metrics,
        execution_backend=execution_backend,
        llm_backend=llm_backend,
        verbose=True,
    )

    results, summary = experiment.run()

    experiment_runs.append(experiment)

    print("=== PER QUERY RESULTS ===")
    for r in results:
        print(r)

    print(f"== SUMMARY {qa} ===")
    for k, v in summary.items():
        print(f"{k}: {v:.4f}")


end_time = time.time()
logging.info(f"Execution time: {int(end_time - start_time)} seconds")

export_experiment_runs(experiment_runs)
