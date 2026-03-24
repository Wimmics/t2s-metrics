import os
import time

from loguru import logger

from t2smetrics.core.eval import JsonlEval
from t2smetrics.core.experiment import Experiment
from t2smetrics.core.export import export_experiment_runs
from t2smetrics.execution.rdflib_backend import RDFLibBackend
from t2smetrics.execution.sparql_endpoint_backend import SparqlEndpointBackend
from t2smetrics.llm.ollama_backend import OllamaBackend
from t2smetrics.metrics.metrics_utils import get_metric_mapping, str_to_metric


def run(
    dataset: str,
    systems_name: list[str],
    jsonl_evals: list[str],
    metrics_str: list[str],
    verbose: bool,
    cache_results: bool,
    export_path: str,
    per_query: bool,
    execution_backend_graph_path: str,
    execution_backend_endpoint_url: str,
    llm_backend_ollama_model: str,
):

    logger.info(f"""Running experiments with the following parameters
    dataset: {dataset}
    Systems: {systems_name}
    JSONL evaluation files: {jsonl_evals}
    Metrics: {metrics_str}
    Verbose mode: {verbose}
    Cache results: {cache_results}
    Export path: {export_path}
    Export per query: {per_query}
    Execution backend graph path: {execution_backend_graph_path}
    Execution backend endpoint URL: {execution_backend_endpoint_url}
    LLM backend Ollama model: {llm_backend_ollama_model}""")

    experiment_runs = []

    if verbose:
        start_time = time.time()

    if "__all__" in metrics_str:
        metrics = list(get_metric_mapping().values())
        llm_backend = OllamaBackend(model=llm_backend_ollama_model)
    else:
        metrics = [str_to_metric(m) for m in metrics_str]
        if "llm_judge" in metrics_str or "__all__" in metrics_str:
            llm_backend = OllamaBackend(model=llm_backend_ollama_model)
        else:
            llm_backend = None

    jsonl_eval_paths = []

    for jsonl_eval_path in jsonl_evals:
        # Check if the path is a directory or a file and create a list of JSONL files to process
        if os.path.isdir(jsonl_eval_path):
            for root, _, files in os.walk(jsonl_eval_path):
                for file in files:
                    if file.endswith(".jsonl"):
                        jsonl_eval_paths.append(os.path.join(root, file))
        elif os.path.isfile(jsonl_eval_path) and jsonl_eval_path.endswith(".jsonl"):
            jsonl_eval_paths.append(jsonl_eval_path)
        else:
            logger.warning(f"Invalid path: {jsonl_eval_path}. Skipping.")

    if execution_backend_endpoint_url:
        execution_backend = SparqlEndpointBackend(execution_backend_endpoint_url)

        if execution_backend_graph_path and execution_backend_endpoint_url:
            logger.warning(
                "Both execution_backend_graph_path and execution_backend_endpoint_url are provided. Using execution_backend_endpoint_url."
            )

    elif execution_backend_graph_path:
        execution_backend = RDFLibBackend(execution_backend_graph_path)

    else:
        raise ValueError(
            "No execution backend provided. Please provide either execution_backend_graph_path or execution_backend_endpoint_url."
        )

    for index, eval in enumerate(jsonl_eval_paths):
        jsonl_eval = JsonlEval(eval)

        qa = (
            systems_name[index]
            if index < len(systems_name)
            else f"System with JSONL {eval}"
        )

        experiment = Experiment(
            dataset=dataset,
            system_name=qa,
            jsonl_eval=jsonl_eval,
            metrics=metrics,
            execution_backend=execution_backend,
            llm_backend=llm_backend,
            verbose=verbose,
            cache_result_sets=cache_results,
        )

        results, summary = experiment.run()

        experiment_runs.append(experiment)

        if per_query:
            logger.info("=== PER QUERY RESULTS ===")
            for r in results:
                logger.info(r)

        logger.info(f"== SUMMARY {qa} ===")
        for k, v in summary.items():
            logger.info(f"{k}: {v:.4f}")

    if verbose:
        end_time = time.time()
        logger.info(f"Execution time: {int(end_time - start_time)} seconds")

    export_experiment_runs(
        experiment_runs, export_path=export_path, per_query=per_query
    )
