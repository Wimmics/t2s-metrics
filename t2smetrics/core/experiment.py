from t2smetrics.aggregation.aggregator import MeanAggregator
from t2smetrics.core.context import EvaluationContext
from t2smetrics.core.engine import EvaluationEngine
from t2smetrics.core.eval import JsonlEval
from t2smetrics.metrics.base import Metric


class Experiment:
    def __init__(
        self,
        jsonl_eval: JsonlEval,
        metrics: list[Metric],
        execution_backend=None,
        llm_backend=None,
        cache_result_sets=True,
        verbose=False,
    ):
        self.jsonl_eval = jsonl_eval

        self.context = EvaluationContext(
            execution_backend=execution_backend,
            llm_backend=llm_backend,
            cache_result_sets=cache_result_sets,
        )

        self.engine = EvaluationEngine(metrics, self.context, verbose=verbose)
        self.aggregator = MeanAggregator()

    def run(self):
        results = self.engine.evaluate(self.jsonl_eval)
        summary = self.aggregator.aggregate(results)
        return results, summary
