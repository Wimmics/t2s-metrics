from langsmith import EvaluationResult

from t2smetrics.aggregation.aggregator import MeanAggregator
from t2smetrics.core.context import EvaluationContext
from t2smetrics.core.engine import EvaluationEngine
from t2smetrics.core.eval import JsonlEval
from t2smetrics.metrics.base import Metric


class Experiment:
    results: set[EvaluationResult] = None
    summary: dict[str, float] = None

    def __init__(
        self,
        jsonl_eval: JsonlEval,
        metrics: list[Metric],
        dataset: str = "unknown",
        system_name: str = "unknown",
        execution_backend=None,
        llm_backend=None,
        cache_result_sets=True,
        verbose=False,
    ):
        """Initialize the experiment with the given parameters.

        Args:
            jsonl_eval (JsonlEval): The evaluation dataset.
            metrics (list[Metric]): The list of metrics to evaluate.
            dataset (str, optional): The name of the dataset. Defaults to "unknown".
            system_name (str, optional): The name of the system being evaluated. Defaults to "unknown".
            execution_backend (optional): The backend to execute SPARQL queries. Defaults to None.
            llm_backend (optional): The backend to execute LLM calls. Defaults to None.
            cache_result_sets (bool, optional): Whether to cache result sets from the execution backend. Defaults to True.
            verbose (bool, optional): Whether to print verbose output during evaluation. Defaults to False.
        """
        self.jsonl_eval = jsonl_eval
        self.dataset = dataset
        self.system_name = system_name
        self.context = EvaluationContext(
            execution_backend=execution_backend,
            llm_backend=llm_backend,
            cache_result_sets=cache_result_sets,
        )

        self.engine = EvaluationEngine(metrics, self.context, verbose=verbose)
        self.aggregator = MeanAggregator()

    def run(
        self, max_workers: int = 1
    ) -> tuple[set[EvaluationResult], dict[str, float]]:
        self.results = self.engine.evaluate(self.jsonl_eval, max_workers=max_workers)
        self.summary = self.aggregator.aggregate(self.results)
        return self.results, self.summary
