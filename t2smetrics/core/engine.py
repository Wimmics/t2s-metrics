from typing import Iterable
from t2smetrics.core.context import EvaluationContext
from t2smetrics.core.dataset import QueryCase
from t2smetrics.measures.base import Measure
from t2smetrics.core.result import EvaluationResult
from tqdm import tqdm


class EvaluationEngine:
    def __init__(
        self, measures: list[Measure], context: EvaluationContext, verbose: bool = False
    ):
        self.measures = measures
        self.context = context
        self.verbose = verbose

    def evaluate(self, dataset: Iterable[QueryCase]) -> list[EvaluationResult]:
        results = []

        for case in tqdm(
            dataset, desc="Evaluating cases", unit="case", disable=not self.verbose
        ):
            for measure in tqdm(
                self.measures,
                desc=f"Evaluating measures of case {case.id}",
                unit="measure",
                disable=not self.verbose,
            ):

                if not case.order_matters and measure.name == "ndcg":
                    continue

                # Enforce requirements
                if (
                    measure.requires_execution
                    and self.context.execution_backend is None
                ):
                    raise RuntimeError(f"{measure.name} requires an execution backend")

                if measure.requires_llm and self.context.llm_backend is None:
                    raise RuntimeError(f"{measure.name} requires an LLM backend")

                results.append(measure.run(case, self.context))

        return results
