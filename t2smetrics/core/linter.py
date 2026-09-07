"""Metric-rule linting and Web Annotation Data Model export."""

import json
import os
import re
import time
import uuid
from dataclasses import dataclass
from typing import Any

from loguru import logger

from t2smetrics import run_experiments
from t2smetrics.core.converter import (
    LABEL_STUDIO_TEMPLATE,
    transform_jsonld_to_labelstudio,
)
from t2smetrics.metrics.metrics_utils import get_metric_mapping


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
    """Parse a lint rule into an AST."""
    if not rule or not rule.strip():
        raise ValueError("Rule must not be empty")
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
    query_uri = f"urn:t2s:query:{experiment.dataset}:{case.id}"
    values_text = ", ".join(f"{name}={metrics[name]}" for name in sorted(metrics))
    target = {
        "id": query_uri,
        "type": "Query",
        "dataset": experiment.dataset,
        "system": experiment.system_name,
        "question": case.question,
        "golden_sparql": case.golden.raw,
        "generated_sparql": case.generated.raw,
        "golden_answerset": _result_set(case.golden_response),
        "generated_answerset": _result_set(case.generated_response),
    }
    return {
        "@context": [
            "http://www.w3.org/ns/anno.jsonld",
            {"t2s": "https://wimmics.github.io/t2s-vocab/"},
        ],
        "id": f"urn:uuid:{uuid.uuid4()}",
        "type": "Annotation",
        "motivation": "assessing",
        "target": target,
        "body": {
            "type": "TextualBody",
            "value": f"Rule failed for query {case.id}: {values_text}",
            "format": "text/plain",
            "purpose": "commenting",
            "rule": rule,
            "metrics": metrics,
        },
    }


def export_wadm_annotations(annotations: list[dict], export_path: str, dataset: str):
    """Write annotations as a WADM Annotation Collection."""
    directory = export_path or f"./datasets/{dataset}/lint"
    if os.path.splitext(directory)[1].lower() in {".json", ".jsonld"}:
        path = directory
    else:
        os.makedirs(directory, exist_ok=True)
        current_time = time.strftime("%Y%m%d-%H%M%S")
        path = os.path.join(directory, f"lint-{dataset}-{current_time}.jsonld")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    document = {
        "@context": [
            "http://www.w3.org/ns/anno.jsonld",
            {"t2s": "https://wimmics.github.io/t2s-vocab/"},
        ],
        "id": f"urn:t2s:lint:{dataset}:{uuid.uuid4()}",
        "type": "AnnotationCollection",
        "items": annotations,
    }
    with open(path, "w", encoding="utf-8") as output:
        json.dump(document, output, indent=2)
    return path


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


def run_lint(
    *,
    dataset,
    systems_name,
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
