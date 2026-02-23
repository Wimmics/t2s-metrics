from t2smetrics.core.context import EvaluationContext
from t2smetrics.core.result import EvaluationResult
from t2smetrics.measures.answer_set.base import AnswerSetMeasure


class HitAtK(AnswerSetMeasure):
    def __init__(self, k=5):
        if k <= 0:
            raise ValueError("k must be a positive integer.")

        self.name = f"Hit@{k}"
        self.k = k

    def compute(self, case, context: EvaluationContext = None):
        gold, pred = self._get_answer_lists(case, context)

        if not self._validate(gold, pred):
            return EvaluationResult(case.id, self.name, 0.0)

        topk = pred[: self.k]
        score = float(any(a in gold for a in topk))
        return EvaluationResult(case.id, self.name, score)
