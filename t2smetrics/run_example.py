from t2smetrics import run_experiments
from t2smetrics.metrics import AnswerSetF1, NaiveCanRougeN

dataset_name = "prob"
graph_endpoint = "http://localhost:8887/"
jsonl_paths = ["./datasets/prob/eval/prob.jsonl"]
metrics = [AnswerSetF1(), NaiveCanRougeN(n=4)]

run_experiments.run(
    dataset=dataset_name,
    jsonl_evals=jsonl_paths,
    metrics_list=metrics,
    execution_backend_endpoint_url=graph_endpoint,
    verbose=True,
    per_query=True,
    safe_limit=3000,
)
