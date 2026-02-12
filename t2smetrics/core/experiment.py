from t2smetrics.core.context import EvaluationContext
from t2smetrics.core.engine import EvaluationEngine
from t2smetrics.aggregation.aggregator import MeanAggregator


class Experiment:
    def __init__(
        self,
        dataset,
        measures,
        execution_backend=None,
        llm_backend=None,
        cache=None,
        verbose=False,
    ):
        self.dataset = dataset

        self.context = EvaluationContext(
            execution_backend=execution_backend,
            llm_backend=llm_backend,
            cache=cache,
        )

        self.engine = EvaluationEngine(measures, self.context, verbose=verbose)
        self.aggregator = MeanAggregator()

    def run(self):
        results = self.engine.evaluate(self.dataset)
        summary = self.aggregator.aggregate(results)
        return results, summary
