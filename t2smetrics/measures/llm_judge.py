from t2smetrics.measures.base import Measure
from t2smetrics.core.result import EvaluationResult


class LLMJudge(Measure):
    name = "llm_judge"
    requires_llm = True

    def compute(self, case, context):
        response = context.llm_backend.judge(
            f"\nGold SPARQL query: {case.golden.raw}\nPredicted SPARQL query: {case.generated.raw}"
        )
        return EvaluationResult(case.id, self.name, response["score"])
