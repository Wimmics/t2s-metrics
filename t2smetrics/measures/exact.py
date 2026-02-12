from t2smetrics.measures.base import Measure
from t2smetrics.core.result import EvaluationResult


class QueryExactMatch(Measure):
    name = "query_exact_match"

    def compute(self, case, context=None):
        score = float(
            case.golden.normalized == case.generated.normalized
        )
        return EvaluationResult(case.id, self.name, score)
