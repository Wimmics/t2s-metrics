from t2smetrics.core.context import EvaluationContext
from t2smetrics.measures.answer_set.base import AnswerSetMeasure
from t2smetrics.core.result import EvaluationResult


class PrecisionAtK(AnswerSetMeasure):

    def __init__(self, k):

        if k < 1:
            raise ValueError("k must be positive integer")

        self.k = k
        self.name = f"p@{k}"

    def compute(self, case, context: EvaluationContext = None):
        gold, pred = self._get_answer_lists(case, context)

        if not self._validate(gold, pred):
            score = 0.0
        else:
            topk = pred[:self.k]
            score = sum(a in gold for a in topk) / self.k

        return EvaluationResult(case.id, self.name, score)
