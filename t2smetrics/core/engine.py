from collections.abc import Iterable
from concurrent.futures import ProcessPoolExecutor, as_completed

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

    def evaluate_case(self, case: QueryCase) -> set[EvaluationResult]:
        case_results = set()

        for metric in tqdm(
            self.metrics,
            desc=f"Evaluating metrics of case {case.id}",
            unit="metric",
            disable=not self.verbose,
        ):
            if not case.order_matters and metric.name == "ndcg":
                continue

            # Enforce requirements
            if metric.requires_execution and self.context.execution_backend is None:
                raise RuntimeError(f"{metric.name} requires an execution backend")

            if metric.requires_llm and self.context.llm_backend is None:
                raise RuntimeError(f"{metric.name} requires an LLM backend")

            result = metric.run(case, self.context)

            case_results.add(result)

        return case_results

    def evaluate(
        self, jsonl_eval: Iterable[QueryCase], max_workers: int = 1
    ) -> set[EvaluationResult]:
        results = set()

        if max_workers > 1:
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(self.evaluate_case, case) for case in jsonl_eval
                ]

                for future in tqdm(
                    as_completed(futures),
                    desc="Evaluating cases",
                    unit="case",
                    total=len(futures),
                    disable=not self.verbose,
                ):
                    case_results = future.result()
                    results.update(case_results)
        else:
            for case in tqdm(
                jsonl_eval,
                desc="Evaluating cases",
                unit="case",
                disable=not self.verbose,
            ):
                case_results = self.evaluate_case(case)
                results.update(case_results)

        return results
