import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from loguru import logger

from t2smetrics.core.eval import JsonlEval
from t2smetrics.core.experiment import Experiment
from t2smetrics.core.export import export_experiment_runs
from t2smetrics.execution.base import ExecutionBackend
from t2smetrics.execution.rdflib_backend import RDFLibBackend
from t2smetrics.execution.sparql_endpoint_backend import SparqlEndpointBackend
from t2smetrics.llm.base import LLMBackend
from t2smetrics.llm.ollama_backend import OllamaBackend
from t2smetrics.metrics.base import Metric
from t2smetrics.metrics.metrics_utils import get_metric_mapping, str_to_metric


def _run_one_experiment(
    eval_path: str,
    dataset: str,
    systems_name: list[str],
    system_index: int,
    metrics: list[Metric],
    execution_backend: ExecutionBackend,
    llm_backend: LLMBackend,
    verbose: bool,
    cache_results: bool,
    per_query: bool,
    max_workers_metrics: int = 1,
):
    jsonl_eval = JsonlEval(eval_path)

    qa = (
        systems_name[system_index]
        if system_index < len(systems_name)
        else f"System with JSONL {eval_path}"
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

    results, summary = experiment.run(max_workers_metrics)

    if per_query:
        logger.info("=== PER QUERY RESULTS ===")
        for r in results:
            logger.info(r)

    logger.info(f"== SUMMARY {qa} ===")
    for k, v in summary.items():
        logger.info(f"{k}: {v:.4f}")

    return experiment


def run(
    jsonl_evals: list[str],
    metrics_list: list[str] | list[Metric],
    export_path: str = None,
    llm_backend_ollama_model: str = "gemma3:4b",
    execution_backend_graph_path: str = None,
    execution_backend_endpoint_url: str = None,
    dataset: str = "unknown",
    systems_name: list[str] = None,
    verbose: bool = False,
    cache_results: bool = True,
    per_query: bool = False,
    parallel: bool = False,
):

    if systems_name is None:
        systems_name = []

    logger.info(f"""Running experiments with the following parameters
    dataset: {dataset}
    Systems: {systems_name}
    JSONL evaluation files: {jsonl_evals}
    Metrics: {metrics_list}
    Verbose mode: {verbose}
    Cache results: {cache_results}
    Export path: {export_path}
    Export per query: {per_query}
    Execution backend graph path: {execution_backend_graph_path}
    Execution backend endpoint URL: {execution_backend_endpoint_url}
    LLM backend Ollama model: {llm_backend_ollama_model}
    Parallel execution: {parallel}
""")

    experiment_runs = []

    if verbose:
        start_time = time.time()

    if (
        type(metrics_list) is list
        and len(metrics_list) > 0
        and isinstance(metrics_list[0], Metric)
    ):
        metrics: list[Metric] = metrics_list

    elif (
        type(metrics_list) is list
        and len(metrics_list) > 0
        and isinstance(metrics_list[0], str)
    ):
        if "__all__" in metrics_list:
            metrics: list[Metric] = list(get_metric_mapping().values())
        else:
            metrics: list[Metric] = [str_to_metric(m) for m in metrics_list]

    if any(m.requires_llm for m in metrics):
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

    if parallel:
        max_cores = os.cpu_count()
        max_workers_qa = min(max_cores, len(jsonl_eval_paths))
        max_workers_metrics = 1  # max(1, max_cores - max_workers_qa) # Currently, we set this to 1 to avoid overloading the system, but it can be adjusted based on the specific use case and system capabilities.

        with ProcessPoolExecutor(max_workers=max_workers_qa) as executor:
            futures = []
            for index, eval_path in enumerate(jsonl_eval_paths):
                futures.append(
                    executor.submit(
                        _run_one_experiment,
                        eval_path=eval_path,
                        dataset=dataset,
                        systems_name=systems_name,
                        system_index=index,
                        metrics=metrics,
                        execution_backend=execution_backend,
                        llm_backend=llm_backend,
                        verbose=verbose,
                        cache_results=cache_results,
                        per_query=per_query,
                        max_workers_metrics=max_workers_metrics,
                    )
                )

            for future in as_completed(futures):
                experiment = future.result()
                experiment_runs.append(experiment)

    else:
        for index, eval_path in enumerate(jsonl_eval_paths):
            experiment = _run_one_experiment(
                eval_path=eval_path,
                dataset=dataset,
                systems_name=systems_name,
                system_index=index,
                metrics=metrics,
                execution_backend=execution_backend,
                llm_backend=llm_backend,
                verbose=verbose,
                cache_results=cache_results,
                per_query=per_query,
            )
            experiment_runs.append(experiment)

    if verbose:
        end_time = time.time()
        logger.info(f"Execution time: {int(end_time - start_time)} seconds")

    export_experiment_runs(
        experiment_runs, export_path=export_path, per_query=per_query
    )
