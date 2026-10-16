"""Export functionality for evaluation results."""

import json
import os
import time
import uuid

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD

from t2smetrics.core.experiment import Experiment

T2S = Namespace("http://ns.inria.fr/t2s/ontology#")
T2SI = Namespace("http://ns.inria.fr/t2s/instance#")
LSQ = Namespace("http://lsq.aksw.org/vocab#")
OA = Namespace("http://www.w3.org/ns/oa#")
SD = Namespace("http://www.w3.org/ns/sparql-service-description#")


def export_experiment_runs(
    experiment_runs: list[Experiment],
    export_path: str = None,
    per_query=False,
    export_format: str = "json",
    endpoint_url: str = None,
):
    """Export the results of multiple experiment runs to a file in the specified format (JSON or Turtle)."""
    if export_format == "json":
        export_experiment_runs_json(
            experiment_runs, export_path=export_path, per_query=per_query
        )
    elif export_format == "ttl":
        export_experiment_runs_turtle(
            experiment_runs,
            export_path=export_path,
            endpoint_url=endpoint_url,
        )
    else:
        raise ValueError(
            f"Unsupported export format: {export_format}. Supported formats are 'json' and 'ttl'."
        )


def export_experiment_runs_json(
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
    """Check the coherence of results across multiple experiment runs.

    This function checks if:
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


def export_experiment_runs_turtle(
    experiment_runs: list[Experiment],
    export_path: str = None,
    endpoint_url: str = None,
) -> str:
    """Export experiment results using the T2S vocabulary.

    The exported graph follows the structure Dataset -> Case -> Query and
    Dataset -> System -> Response -> Score.
    """
    check_coherence_of_results(experiment_runs)

    if export_path is None:
        export_path = f"./datasets/{experiment_runs[0].dataset}/results"

    current_time = time.strftime("%Y%m%d-%H%M%S")
    experiment_id = f"{experiment_runs[0].dataset}-{current_time}"
    export_path += f"/{experiment_id}.ttl"

    base_uri = URIRef(f"urn:uuid:{uuid.uuid4()}")
    dataset_uri = _uuid_uri()
    system_uris = {
        experiment.system_name: _uuid_uri() for experiment in experiment_runs
    }

    g = Graph()
    g.bind("t2s", T2S)
    g.bind("t2si", T2SI)
    g.bind("lsq", LSQ)
    g.bind("oa", OA)
    g.bind("sd", SD)
    g.bind("xsd", XSD)
    g.bind("rdfs", RDFS)
    g.bind("", base_uri)

    g.add((dataset_uri, RDF.type, T2S.Dataset))
    g.add((dataset_uri, RDFS.label, Literal(experiment_runs[0].dataset)))

    for run_index, experiment in enumerate(experiment_runs):
        system_uri = system_uris[experiment.system_name]
        experiment_uri = _uuid_uri()
        g.add((system_uri, RDF.type, T2S.System))
        g.add((system_uri, RDFS.label, Literal(experiment.system_name)))
        g.add((system_uri, T2S.participatesIn, experiment_uri))
        g.add((experiment_uri, RDF.type, T2S.Experiment))
        g.add((experiment_uri, T2S.evaluatedOn, dataset_uri))
        if endpoint_url is not None:
            g.add(
                (
                    experiment_uri,
                    T2S.usedEndpoint,
                    Literal(endpoint_url, datatype=XSD.anyURI),
                )
            )

        for metric_name, metric_value in experiment.summary.items():
            score_uri = _uuid_uri()
            metric_uri = _metric_uri(metric_name)
            g.add((metric_uri, RDF.type, T2S.Metric))
            g.add((metric_uri, RDFS.label, Literal(metric_name)))
            g.add((score_uri, RDF.type, T2S.Score))
            g.add((score_uri, T2S.forMetric, metric_uri))
            g.add(
                (score_uri, T2S.scoreValue, Literal(metric_value, datatype=XSD.decimal))
            )
            _add_score_annotation(g, experiment_uri, score_uri)

        for case in experiment.cases or []:
            case_uri = _uuid_uri()
            g.add((dataset_uri, T2S.hasCase, case_uri))
            g.add((case_uri, RDF.type, T2S.Case))
            g.add((case_uri, T2S.caseID, Literal(case.id)))
            # TODO add appropriate language tag if available
            g.add((case_uri, T2S.question, Literal(case.question, lang="en")))
            gold_query_uri = _uuid_uri()
            g.add((case_uri, T2S.hasGoldQuery, gold_query_uri))
            _add_query(g, gold_query_uri, case.golden.raw, case.golden_response)

            response_uri = _uuid_uri()
            generated_query_uri = _uuid_uri()
            g.add((system_uri, T2S.providedResponse, response_uri))
            g.add((response_uri, RDF.type, T2S.Response))
            g.add((response_uri, T2S.isResponseTo, case_uri))
            g.add((response_uri, T2S.hasGeneratedQuery, generated_query_uri))
            _add_query(
                g,
                generated_query_uri,
                case.generated.raw,
                case.generated_response,
            )

            for result in experiment.results or []:
                if result.id != case.id:
                    continue
                score_uri = _uuid_uri()
                metric_uri = _metric_uri(result.metric)
                g.add((metric_uri, RDF.type, T2S.Metric))
                g.add((metric_uri, RDFS.label, Literal(result.metric)))
                g.add((score_uri, RDF.type, T2S.Score))
                g.add((score_uri, T2S.forMetric, metric_uri))
                g.add(
                    (
                        score_uri,
                        T2S.scoreValue,
                        Literal(result.score, datatype=XSD.decimal),
                    )
                )
                _add_score_annotation(g, response_uri, score_uri)

    # Serialize to Turtle
    turtle_output = g.serialize(format="turtle", encoding="utf-8").decode("utf-8")

    # Save to file if path provided
    if export_path:
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(turtle_output)

    return turtle_output


def _uuid_uri() -> URIRef:
    """Return a UUID URN for an exported resource."""
    return URIRef(f"urn:uuid:{uuid.uuid4()}")


def _metric_uri(metric_name: str) -> URIRef:
    normalized_name = "".join(
        character if character.isalnum() or character in "-_" else "_"
        for character in metric_name.lower()
    )
    return URIRef(T2SI[normalized_name])


def _add_query(graph, query_uri, query, response):
    graph.add((query_uri, RDF.type, T2S.Query))
    graph.add((query_uri, T2S.queryText, Literal(str(query))))
    if response != "__NOT_CACHED__":
        result_set_uri = _uuid_uri()
        graph.add((query_uri, T2S.hasResultSet, result_set_uri))
        graph.add((result_set_uri, RDF.type, T2S.ResultSet))
        graph.add(
            (
                result_set_uri,
                T2S.resultSetValueJSON,
                Literal(json.dumps(response, default=str, sort_keys=True)),
            )
        )


def _add_score_annotation(graph, target_uri, score_uri):
    annotation_uri = _uuid_uri()
    graph.add((annotation_uri, RDF.type, T2S.Annotation))
    graph.add((annotation_uri, OA.motivation, Literal("assessing")))
    graph.add((annotation_uri, T2S.hasTarget, target_uri))
    graph.add((annotation_uri, T2S.hasBody, score_uri))
