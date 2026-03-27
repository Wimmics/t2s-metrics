"""Export functionality for evaluation results."""

import json
import os
import time

from t2smetrics.core.experiment import Experiment


def export_experiment_runs(
    experiment_runs: list[Experiment], export_path: str = None, per_query=False
):
    """Export the results of multiple experiment runs to a JSON file."""

    check_coherence_of_results(experiment_runs)

    if export_path is None:
        export_path = f"./datasets/{experiment_runs[0].dataset}/results"

    current_time = time.strftime("%Y%m%d-%H%M%S")
    export_path += f"/{experiment_runs[0].dataset}-{current_time}.json"

    all_qa_results = []
    for experiment in experiment_runs:
        qa_result = {
            "dataset": experiment.dataset,
            "system_name": experiment.system_name,
            "metrics": experiment.summary,
        }
        if per_query:
            qa_result["per_query_results"] = [r.to_dict() for r in experiment.results]

        all_qa_results.append(qa_result)

    os.makedirs(os.path.dirname(export_path), exist_ok=True)

    with open(export_path, "w") as f:
        json.dump(all_qa_results, f, indent=2)


def check_coherence_of_results(experiment_runs: list[Experiment], per_query=False):
    """Check the coherence of results across multiple experiment runs. This function checks if:
    - the same dataset is present in all experiment runs.
    - if a summary of results is present for all experiment runs.
    - if per_query is True, check that per-query results are present for all experiment runs

    If any inconsistency is found, a ValueError is raised.


    Args:
        experiment_runs: A list of Experiment instances to check for coherence.
        per_query: A boolean flag indicating whether to check for the presence of per-query results.
    """

    if experiment_runs is None or len(experiment_runs) == 0:
        raise ValueError("No experiment runs to export.")

    dataset = experiment_runs[0].dataset
    for experiment in experiment_runs:
        if experiment.dataset != dataset:
            raise ValueError(
                f"Inconsistent dataset in experiment runs: expected {dataset}, got {experiment.dataset}"
            )
        if experiment.summary is None:
            raise ValueError(
                f"Experiment run for system {experiment.system_name} does not have a summary of results. Run the experiment to compute the summary before exporting."
            )
        if per_query and experiment.results is None:
            raise ValueError(
                f"Experiment run for system {experiment.system_name} does not have per-query results. Run the experiment to compute the per-query results before exporting."
            )
