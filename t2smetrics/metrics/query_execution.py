from t2smetrics.metrics.base import Metric
from t2smetrics.core.result import EvaluationResult


class QueryExecution(Metric):
    name = "query_execution"
    requires_execution = True

    def compute(self, case, context):
        try:
            answer = context.execution_backend.execute(case.generated.raw)
            score = 1.0 if answer is not None else 0.0
        except Exception:
            score = 0.0

        return EvaluationResult(case.id, self.name, score)
