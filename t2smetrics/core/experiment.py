from langsmith import EvaluationResult

from t2smetrics.aggregation.aggregator import MeanAggregator
from t2smetrics.core.context import EvaluationContext
from t2smetrics.core.engine import EvaluationEngine
from t2smetrics.core.eval import JsonlEval
from t2smetrics.metrics.base import Metric
from t2smetrics.representation.preprocessing import prefix_preprocessor


class Experiment:
    results: set[EvaluationResult] = None
    summary: dict[str, float] = None
    cases: list = None

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
        add_popular_prefixes=False,
        add_custom_prefixes=None,
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
            add_popular_prefixes (bool, optional): Whether to add popular prefixes. Defaults to False.
            add_custom_prefixes (dict, optional): Prefixes to add to queries. Defaults to None.
        """
        self.jsonl_eval = jsonl_eval
        self.dataset = dataset
        self.system_name = system_name
        self.context = EvaluationContext(
            execution_backend=execution_backend,
            llm_backend=llm_backend,
            cache_result_sets=cache_result_sets,
        )
        self.prefix_preprocessor = prefix_preprocessor(
            add_popular_prefixes=add_popular_prefixes,
            add_custom_prefixes=add_custom_prefixes,
        )

        self.engine = EvaluationEngine(metrics, self.context, verbose=verbose)
        self.aggregator = MeanAggregator()

    def run(
        self, max_workers: int = 1
    ) -> tuple[set[EvaluationResult], dict[str, float]]:
        self.cases = list(self.jsonl_eval)
        self.cases = [self.prefix_preprocessor.apply(case) for case in self.cases]
        self.results = self.engine.evaluate(self.cases, max_workers=max_workers)
        self.summary = self.aggregator.aggregate(self.results)
        return self.results, self.summary
