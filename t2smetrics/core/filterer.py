"""Metric-rule filtering and Web Annotation Data Model export."""

import json
import os
import re
import time
import uuid
from dataclasses import dataclass
from typing import Any

from loguru import logger
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD

from t2smetrics import run_experiments
from t2smetrics.core.converter import (
    LABEL_STUDIO_TEMPLATE,
    transform_jsonld_to_labelstudio,
)
from t2smetrics.metrics.metrics_utils import get_metric_mapping

T2S = Namespace("http://ns.inria.fr/t2s/ontology#")
T2SI = Namespace("http://ns.inria.fr/t2s/instance#")
OA = Namespace("http://www.w3.org/ns/oa#")
LSQ = Namespace("http://lsq.aksw.org/vocab#")
SD = Namespace("http://www.w3.org/ns/sparql-service-description#")

BASIC_RULE_TEXT = (
    "((answerset_f1[0] && naive-can-rouge-4[0.95,1]) || "
    "(answerset_f1[1] && naive-can-rouge-4[0,0.25]) || "
    "(answerset_f1[0,0.5] && f1_spinach[1]))"
)


@dataclass(frozen=True)
class Comparison:
    """A comparison of a metric value against a range."""

    metric: str
    lower: float
    upper: float
    include_lower: bool = True
    include_upper: bool = True

    def evaluate(self, value: float) -> bool:
        """Evaluate the comparison against a given value.

        Args:
            value (float): The metric value to evaluate.

        Returns:
            bool: True if the value is within the range, False otherwise.
        """
        lower_ok = value >= self.lower if self.include_lower else value > self.lower
        upper_ok = value <= self.upper if self.include_upper else value < self.upper
        return lower_ok and upper_ok


class _RuleParser:
    _metric = re.compile(r"[A-Za-z0-9_-]+")
    _number = re.compile(r"(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")

    def __init__(self, text: str):
        self.text = text
        self.position = 0

    def parse(self):
        value = self._parse_or()
        self._spaces()
        if self.position != len(self.text):
            raise ValueError(f"Unexpected rule text at position {self.position}")
        return value

    def _parse_or(self):
        value = self._parse_and()
        while self._consume("||"):
            value = ("or", value, self._parse_and())
        return value

    def _parse_and(self):
        value = self._parse_atom()
        while self._consume("&&"):
            value = ("and", value, self._parse_atom())
        return value

    def _parse_atom(self):
        self._spaces()
        if self._consume("("):
            value = self._parse_or()
            if not self._consume(")"):
                raise ValueError("Missing closing ')' in rule")
            return value

        metric_match = self._metric.match(self.text, self.position)
        if not metric_match:
            raise ValueError(
                f"Expected metric at position {self.position} found: {self.text[self.position :]}"
            )
        metric = metric_match.group()
        self.position = metric_match.end()
        self._spaces()
        opening = self._take("[") or self._take("]")
        if opening is None:
            raise ValueError(f"Expected '[' or ']' after metric {metric}")
        lower = self._read_number()
        self._spaces()
        if self._consume("]"):
            return Comparison(metric, lower, lower, opening == "[")
        if not self._consume(","):
            raise ValueError("Expected ',' or ']' in metric range")
        upper = self._read_number()
        self._spaces()
        closing = self._take("]") or self._take("[")
        if closing is None:
            raise ValueError("Expected ']' or '[' at the end of metric range")
        return Comparison(metric, lower, upper, opening == "[", closing == "]")

    def _read_number(self) -> float:
        self._spaces()
        match = self._number.match(self.text, self.position)
        if not match:
            raise ValueError(f"Expected number at position {self.position}")
        self.position = match.end()
        return float(match.group())

    def _spaces(self):
        while self.position < len(self.text) and self.text[self.position].isspace():
            self.position += 1

    def _consume(self, token: str) -> bool:
        self._spaces()
        if self.text.startswith(token, self.position):
            self.position += len(token)
            return True
        return False

    def _take(self, token: str) -> str | None:
        self._spaces()
        if self.text.startswith(token, self.position):
            self.position += len(token)
            return token
        return None


def parse_rule(rule: str):
    """Parse a filter rule into an AST."""
    if not rule or not rule.strip():
        raise ValueError("Rule must not be empty")
    if rule == "basicRule":
        rule = BASIC_RULE_TEXT
    return _RuleParser(rule).parse()


def referenced_metrics(ast) -> set[str]:
    """Return metric names used by a parsed rule."""
    if isinstance(ast, Comparison):
        return {ast.metric}
    return referenced_metrics(ast[1]) | referenced_metrics(ast[2])


def evaluate_rule(ast, values: dict[str, float]) -> bool:
    """Evaluate a parsed rule against per-query metric values."""
    if isinstance(ast, Comparison):
        if ast.metric not in values:
            logger.warning(
                f"Metric {ast.metric!r} was not computed for the ast {ast!r} returning False"
            )
            return False
        return ast.evaluate(values[ast.metric])
    left = evaluate_rule(ast[1], values)
    right = evaluate_rule(ast[2], values)
    return (left or right) if ast[0] == "or" else (left and right)


def _result_set(response: Any):
    if response in (None, "__NOT_CACHED__"):
        return None
    if isinstance(response, dict):
        return response
    return response.convert() if hasattr(response, "convert") else response


def _annotation(experiment, case, metrics, rule):
    return {
        "annotation_uri": _uuid_uri(),
        "dataset": experiment.dataset,
        "system": experiment.system_name,
        "case_id": case.id,
        "question": case.question,
        "golden_query": case.golden.raw,
        "generated_query": case.generated.raw,
        "golden_response": case.golden_response,
        "generated_response": case.generated_response,
        "metrics": metrics,
        "rule": rule,
    }


def export_wadm_annotations(annotations: list[dict], export_path: str, dataset: str):
    """Write annotations using the v2 vocabulary in Turtle."""
    directory = export_path or f"./datasets/{dataset}/filter"
    if os.path.splitext(directory)[1].lower() == ".ttl":
        path = directory
    else:
        os.makedirs(directory, exist_ok=True)
        current_time = time.strftime("%Y%m%d-%H%M%S")
        path = os.path.join(directory, f"filter-{dataset}-{current_time}.ttl")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    graph = Graph()
    graph.bind("t2s", T2S)
    graph.bind("t2si", T2SI)
    graph.bind("oa", OA)
    graph.bind("lsq", LSQ)
    graph.bind("sd", SD)
    graph.bind("xsd", XSD)
    graph.bind("rdfs", RDFS)
    dataset_uri = _named_uri("dataset", dataset)
    graph.add((dataset_uri, RDF.type, T2S.Dataset))
    graph.add((dataset_uri, RDFS.label, Literal(dataset)))
    for annotation in annotations:
        _add_annotation(graph, dataset_uri, annotation)

    with open(path, "w", encoding="utf-8") as output:
        output.write(graph.serialize(format="turtle"))
    return path


def _uuid_uri() -> URIRef:
    return URIRef(f"urn:uuid:{uuid.uuid4()}")


def _named_uri(resource_type: str, value: str) -> URIRef:
    return URIRef(f"urn:t2s:{resource_type}:{value}")


def _rule_uri(graph: Graph, rule: str) -> URIRef:
    if rule in {"basicRule", BASIC_RULE_TEXT}:
        return T2SI.basicRule
    rule_uri = _uuid_uri()
    graph.add((rule_uri, RDF.type, T2S.RuleExpression))
    graph.add((rule_uri, T2S.ruleText, Literal(rule)))
    return rule_uri


def _metric_uri(metric_name: str) -> URIRef:
    normalized_name = "".join(
        character if character.isalnum() or character in "-_" else "_"
        for character in metric_name.lower()
    )
    return URIRef(T2SI[normalized_name])


def _add_annotation(graph: Graph, dataset_uri: URIRef, annotation: dict):
    system_uri = _named_uri("system", annotation["system"])
    case_uri = _named_uri("case", f"{annotation['dataset']}:{annotation['case_id']}")
    experiment_uri = _uuid_uri()
    response_uri = _uuid_uri()
    generated_query_uri = _uuid_uri()
    gold_query_uri = _uuid_uri()
    error_uri = _uuid_uri()

    graph.add((system_uri, RDF.type, T2S.System))
    graph.add((system_uri, RDFS.label, Literal(annotation["system"])))
    graph.add((system_uri, T2S.participatesIn, experiment_uri))
    graph.add((experiment_uri, RDF.type, T2S.Experiment))
    graph.add((experiment_uri, T2S.evaluatedOn, dataset_uri))
    graph.add((dataset_uri, T2S.hasCase, case_uri))
    graph.add((case_uri, RDF.type, T2S.Case))
    graph.add((case_uri, T2S.caseID, Literal(str(annotation["case_id"]))))
    graph.add((case_uri, T2S.question, Literal(annotation["question"], lang="en")))
    graph.add((case_uri, T2S.hasGoldQuery, gold_query_uri))
    _add_query(
        graph, gold_query_uri, annotation["golden_query"], annotation["golden_response"]
    )
    graph.add((system_uri, T2S.providedResponse, response_uri))
    graph.add((response_uri, RDF.type, T2S.Response))
    graph.add((response_uri, T2S.isResponseTo, case_uri))
    graph.add((response_uri, T2S.hasGeneratedQuery, generated_query_uri))
    _add_query(
        graph,
        generated_query_uri,
        annotation["generated_query"],
        annotation["generated_response"],
    )

    graph.add((annotation["annotation_uri"], RDF.type, T2S.Annotation))
    graph.add((annotation["annotation_uri"], OA.motivation, Literal("assessing")))
    graph.add((annotation["annotation_uri"], T2S.hasTarget, response_uri))
    graph.add((annotation["annotation_uri"], T2S.hasBody, error_uri))
    graph.add((error_uri, RDF.type, T2S.ProfilingError))
    graph.add((error_uri, T2S.usedRule, _rule_uri(graph, annotation["rule"])))

    for metric_name, metric_value in annotation["metrics"].items():
        metric_uri = _metric_uri(metric_name)
        score_uri = _uuid_uri()
        score_annotation_uri = _uuid_uri()
        graph.add((metric_uri, RDF.type, T2S.Metric))
        graph.add((metric_uri, RDFS.label, Literal(metric_name)))
        graph.add((score_uri, RDF.type, T2S.Score))
        graph.add((score_uri, T2S.forMetric, metric_uri))
        graph.add(
            (score_uri, T2S.scoreValue, Literal(metric_value, datatype=XSD.decimal))
        )
        graph.add((score_annotation_uri, RDF.type, T2S.Annotation))
        graph.add((score_annotation_uri, OA.motivation, Literal("assessing")))
        graph.add((score_annotation_uri, T2S.hasTarget, response_uri))
        graph.add((score_annotation_uri, T2S.hasBody, score_uri))


def _add_query(graph: Graph, query_uri: URIRef, query: str, response: Any):
    graph.add((query_uri, RDF.type, T2S.Query))
    graph.add((query_uri, T2S.queryText, Literal(str(query))))
    result_set = _result_set(response)
    if result_set is not None:
        result_set_uri = _uuid_uri()
        graph.add((query_uri, T2S.hasResultSet, result_set_uri))
        graph.add((result_set_uri, RDF.type, T2S.ResultSet))
        graph.add(
            (
                result_set_uri,
                T2S.resultSetValueJSON,
                Literal(json.dumps(result_set, default=str, sort_keys=True)),
            )
        )


def export_labelstudio_annotations(
    source_path: str,
    export_path: str | None,
    dataset: str,
) -> str:
    """Read a WADM JSON-LD export and convert it to Label Studio JSON."""
    with open(source_path, encoding="utf-8") as source:
        jsonld_content = source.read()

    converted = transform_jsonld_to_labelstudio(jsonld_content)

    if export_path:
        if os.path.splitext(export_path)[1].lower() in {".json", ".jsonld"}:
            target = export_path
            if os.path.splitext(target)[1].lower() == ".jsonld":
                target = os.path.splitext(target)[0] + ".json"
        else:
            os.makedirs(export_path, exist_ok=True)
            basename = os.path.splitext(os.path.basename(source_path))[0]
            target = os.path.join(export_path, f"{basename}-label-studio.json")
    else:
        directory = f"./datasets/{dataset}/label-studio"
        os.makedirs(directory, exist_ok=True)
        basename = os.path.splitext(os.path.basename(source_path))[0]
        target = os.path.join(directory, f"{basename}-label-studio.json")

    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)

    # Write the converted Label Studio JSON file
    with open(target, "w", encoding="utf-8") as output:
        output.write(converted)

    # Write the Label Studio template XML file alongside the converted JSON
    with open(
        os.path.splitext(target)[0] + "-template.xml",
        "w",
        encoding="utf-8",
    ) as output:
        output.write(LABEL_STUDIO_TEMPLATE)
    return target


def run_filter(
    *,
    dataset,
    systems_name=None,
    rule,
    jsonl_evals=None,
    export_path=None,
    verbose=False,
    cache_results=True,
    execution_backend_graph_path=None,
    execution_backend_endpoint_url=None,
    llm_backend_ollama_model="gemma3:4b",
    parallel=False,
    convert=None,
    safe_limit=0,
    add_popular_prefixes=False,
    add_custom_prefixes=None,
):
    """Compute metrics, flag matching cases, and export a WADM report."""
    ast = parse_rule(rule)
    names = referenced_metrics(ast)
    unknown = names - set(get_metric_mapping())

    if unknown:
        raise ValueError(f"Unknown metric name(s): {', '.join(sorted(unknown))}")

    experiments = run_experiments.run(
        jsonl_evals=jsonl_evals,
        metrics_list=[get_metric_mapping()[name] for name in sorted(names)],
        dataset=dataset,
        systems_name=systems_name,
        verbose=verbose,
        cache_results=cache_results,
        execution_backend_graph_path=execution_backend_graph_path,
        execution_backend_endpoint_url=execution_backend_endpoint_url,
        llm_backend_ollama_model=llm_backend_ollama_model,
        parallel=parallel,
        per_query=True,
        export_results=False,
        safe_limit=safe_limit,
        add_popular_prefixes=add_popular_prefixes,
        add_custom_prefixes=add_custom_prefixes,
    )
    annotations = []
    for experiment in experiments:
        by_query = {}
        for result in experiment.results:
            by_query.setdefault(result.id, {})[result.metric] = result.score
        cases = {case.id: case for case in experiment.cases}
        for query_id, values in by_query.items():
            if evaluate_rule(ast, values):
                annotations.append(
                    _annotation(experiment, cases[query_id], values, rule)
                )
    path = export_wadm_annotations(annotations, export_path, dataset)
    if convert == "label-studio":
        converted_path = export_labelstudio_annotations(path, export_path, dataset)
        return converted_path
    return path
