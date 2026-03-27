from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.base import Metric


class QueryExactMatch(Metric):
    name = "query_exact_match"

    def compute(self, case, context=None):
        score = float(
            case.golden.normalized == case.generated.normalized
        )
        return EvaluationResult(case.id, self.name, score)
