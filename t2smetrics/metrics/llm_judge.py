from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.base import Metric


class LLMJudge(Metric):
    name = "llm_judge"
    requires_llm = True

    def compute(self, case, context):
        response = context.llm_backend.judge(
            f"\nGold SPARQL query: {case.golden.raw}\nPredicted SPARQL query: {case.generated.raw}"
        )
        score = response["score"] if "score" in response and isinstance(response["score"], (int, float)) else 0.0
        return EvaluationResult(case.id, self.name, score)
