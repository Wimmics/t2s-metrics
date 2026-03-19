from collections.abc import Iterable

from tqdm import tqdm

from t2smetrics.core.context import EvaluationContext
from t2smetrics.core.eval import QueryCase
from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.base import Metric


class EvaluationEngine:
    def __init__(
        self, metrics: list[Metric], context: EvaluationContext, verbose: bool = False
    ):
        self.metrics = metrics
        self.context = context
        self.verbose = verbose

    def evaluate(self, jsonl_eval: Iterable[QueryCase]) -> set[EvaluationResult]:
        results = set()

        for case in tqdm(
            jsonl_eval, desc="Evaluating cases", unit="case", disable=not self.verbose
        ):
            for metric in tqdm(
                self.metrics,
                desc=f"Evaluating metrics of case {case.id}",
                unit="metric",
                disable=not self.verbose,
            ):

                if not case.order_matters and metric.name == "ndcg":
                    continue

                # Enforce requirements
                if (
                    metric.requires_execution
                    and self.context.execution_backend is None
                ):
                    raise RuntimeError(f"{metric.name} requires an execution backend")

                if metric.requires_llm and self.context.llm_backend is None:
                    raise RuntimeError(f"{metric.name} requires an LLM backend")

                results.add(metric.run(case, self.context))

        return results
