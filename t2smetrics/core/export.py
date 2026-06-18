"""Export functionality for evaluation results."""

import json
import os
import time
from datetime import datetime

from rdflib import RDFS, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, FOAF, PROV, RDF, XSD

from t2smetrics.core.experiment import Experiment


def export_experiment_runs(
    experiment_runs: list[Experiment],
    export_path: str = None,
    per_query=False,
    export_format: str = "json",
):
    """Export the results of multiple experiment runs to a file in the specified format (JSON or Turtle)."""
    if export_format == "json":
        export_experiment_runs_json(
            experiment_runs, export_path=export_path, per_query=per_query
        )
    elif export_format == "ttl":
        export_experiment_runs_turtle(
            experiment_runs, export_path=export_path, per_query=per_query
        )
    else:
        raise ValueError(
            f"Unsupported export format: {export_format}. Supported formats are 'json' and 'ttl'."
        )


def export_experiment_runs_json(
    experiment_runs: list[Experiment],
    export_path: str = None,
    per_query=False,
    export_format: str = "json",
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


DCAT = Namespace("http://www.w3.org/ns/dcat#")
T2S = Namespace("https://wimmics.github.io/t2s-metrics/metrics#")


def export_experiment_runs_turtle(
    experiment_runs: list[Experiment],
    export_path: str = None,
    per_query: bool = False,
    base_url: str = "https://example.org/experiments",
) -> str:
    """Export experiment results as Turtle with rich metadata using DCAT, PROV, etc.

    Returns a Turtle string that can be saved to a file.
    """
    check_coherence_of_results(experiment_runs)

    if export_path is None:
        export_path = f"./datasets/{experiment_runs[0].dataset}/results"

    current_time = time.strftime("%Y%m%d-%H%M%S")
    experiment_id = f"{experiment_runs[0].dataset}-{current_time}"
    export_path += f"/{experiment_id}.ttl"

    # Create base URIs
    base_uri = URIRef(f"{base_url}/{experiment_id}")
    dataset_uri = URIRef(f"{base_uri}/dataset")
    experiment_uri = URIRef(f"{base_uri}/experiment")
    agent_uri = URIRef(f"{base_uri}/agent")

    # Create RDF graph
    g = Graph()

    # Bind namespaces for cleaner output
    g.bind("dcat", DCAT)
    g.bind("prov", PROV)
    g.bind("dcterms", DCTERMS)
    g.bind("t2sm", T2S)
    g.bind("foaf", FOAF)
    g.bind("xsd", XSD)
    g.bind("", base_uri)  # Default namespace

    # 1. Dataset node (DCAT)
    g.add((dataset_uri, RDF.type, DCAT.Dataset))
    g.add((dataset_uri, RDF.type, PROV.Entity))
    g.add(
        (
            dataset_uri,
            DCTERMS.title,
            Literal(
                f"Evaluation Results for {experiment_runs[0].dataset}",
                lang="en",
            ),
        )
    )
    g.add(
        (
            dataset_uri,
            DCTERMS.description,
            Literal(
                f"Question answering evaluation results for dataset {experiment_runs[0].dataset}",
                lang="en",
            ),
        )
    )
    g.add(
        (
            dataset_uri,
            DCTERMS.issued,
            Literal(datetime.now().isoformat(), datatype=XSD.dateTime),
        )
    )
    g.add((dataset_uri, DCTERMS.identifier, Literal(experiment_runs[0].dataset)))
    g.add((dataset_uri, DCAT.keyword, Literal("evaluation")))
    g.add((dataset_uri, DCAT.keyword, Literal("question-answering")))
    g.add((dataset_uri, DCAT.keyword, Literal("benchmark")))

    # 2. Experiment node (PROV Activity)
    g.add((experiment_uri, RDF.type, PROV.Activity))
    g.add((experiment_uri, RDF.type, DCAT.DataService))
    g.add(
        (
            experiment_uri,
            PROV.startedAtTime,
            Literal(datetime.now().isoformat(), datatype=XSD.dateTime),
        )
    )
    g.add(
        (
            experiment_uri,
            DCTERMS.title,
            Literal(f"Evaluation Run - {experiment_id}", lang="en"),
        )
    )
    g.add(
        (
            experiment_uri,
            DCTERMS.description,
            Literal("Question answering system evaluation experiment", lang="en"),
        )
    )
    g.add((experiment_uri, PROV.used, dataset_uri))

    # 3. Agent node (PROV Agent)
    g.add((agent_uri, RDF.type, PROV.Agent))
    g.add((agent_uri, RDF.type, FOAF.Agent))
    g.add((agent_uri, FOAF.name, Literal("Evaluation System")))
    g.add((agent_uri, RDFS.comment, Literal("Automated QA evaluation system")))

    # 4. Create nodes for each experiment run
    for idx, experiment in enumerate(experiment_runs):
        run_uri = URIRef(f"{base_uri}/run/{idx}")
        result_uri = URIRef(f"{run_uri}/results")

        # Create experiment run node
        g.add((run_uri, RDF.type, PROV.Entity))
        g.add((run_uri, RDF.type, DCAT.Distribution))
        g.add((run_uri, DCTERMS.title, Literal(f"Experiment Run {idx + 1}", lang="en")))
        g.add(
            (
                run_uri,
                DCTERMS.description,
                Literal(f"Run using system: {experiment.system_name}", lang="en"),
            )
        )
        g.add((run_uri, PROV.wasGeneratedBy, experiment_uri))
        g.add((run_uri, PROV.wasAttributedTo, agent_uri))
        g.add((run_uri, T2S.systemName, Literal(experiment.system_name)))
        g.add((run_uri, T2S.dataset, Literal(experiment.dataset)))

        # Add metrics
        for metric_name, metric_value in experiment.summary.items():
            # Convert metric name to valid property
            prop_name = metric_name.lower().replace(" ", "_")
            prop_name = metric_name.lower().replace("@", "_")
            if isinstance(metric_value, (int, float)):
                g.add(
                    (
                        run_uri,
                        T2S[prop_name],
                        Literal(metric_value, datatype=XSD.float),
                    )
                )
            else:
                g.add((run_uri, T2S[prop_name], Literal(str(metric_value))))

        # Add per-query results if requested
        if per_query and hasattr(experiment, "results"):
            per_query_uri = URIRef(f"{result_uri}/per_query")

            g.add((per_query_uri, RDF.type, PROV.Collection))
            g.add((per_query_uri, RDF.type, T2S.ItemList))
            g.add((per_query_uri, T2S.name, Literal("Per-Query Results")))
            g.add(
                (
                    per_query_uri,
                    T2S.description,
                    Literal(f"Detailed results for each query in {experiment.dataset}"),
                )
            )
            g.add(
                (
                    per_query_uri,
                    T2S.numberOfItems,
                    Literal(len(experiment.results), datatype=XSD.integer),
                )
            )

            for q_idx, result in enumerate(experiment.results):
                query_uri = URIRef(f"{per_query_uri}/query/{q_idx}")
                result_dict = result.to_dict() if hasattr(result, "to_dict") else result

                g.add((query_uri, RDF.type, T2S.Question))
                g.add(
                    (
                        query_uri,
                        T2S.position,
                        Literal(q_idx + 1, datatype=XSD.integer),
                    )
                )

                if "question" in result_dict:
                    g.add(
                        (
                            query_uri,
                            T2S.question,
                            Literal(str(result_dict["question"])),
                        )
                    )
                if "answer" in result_dict:
                    g.add((query_uri, T2S.answer, Literal(str(result_dict["answer"]))))
                if "context" in result_dict:
                    g.add(
                        (
                            query_uri,
                            T2S.isBasedOn,
                            Literal(str(result_dict["context"])),
                        )
                    )

                # Add any metrics per query
                for key, value in result_dict.items():
                    if key not in ["question", "answer", "context"]:
                        prop_name = key.lower().replace(" ", "_")
                        if isinstance(value, (int, float)):
                            g.add(
                                (
                                    query_uri,
                                    T2S[prop_name],
                                    Literal(value, datatype=XSD.float),
                                )
                            )
                        else:
                            g.add((query_uri, T2S[prop_name], Literal(str(value))))

                g.add((per_query_uri, T2S.itemListElement, query_uri))

            g.add((run_uri, DCAT.hasPart, per_query_uri))

        # Link run to dataset
        g.add((dataset_uri, DCAT.distribution, run_uri))
        g.add((experiment_uri, PROV.generated, run_uri))

    # Serialize to Turtle
    turtle_output = g.serialize(format="turtle", encoding="utf-8").decode("utf-8")

    # Save to file if path provided
    if export_path:
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(turtle_output)

    return turtle_output


def export_experiment_runs_turtle_wrapper(
    experiment_runs: list[Experiment], export_path: str = None, per_query: bool = False
) -> str:
    """Wrapper that saves Turtle file and returns the path."""
    result = export_experiment_runs_turtle(experiment_runs, export_path, per_query)

    if export_path is None:
        export_path = f"./datasets/{experiment_runs[0].dataset}/results"

    current_time = time.strftime("%Y%m%d-%H%M%S")
    export_path += f"/{experiment_runs[0].dataset}-{current_time}.ttl"

    return export_path
