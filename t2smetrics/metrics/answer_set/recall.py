from t2smetrics.metrics.answer_set.base import AnswerSetMeasure
from t2smetrics.core.result import EvaluationResult


class AnswerSetRecall(AnswerSetMeasure):
    name = "answerset_recall"

    def compute(self, case, context):
        gold, pred = self._get_answer_sets(case, context)

        if not gold:
            score = 1.0  # convention: perfectly recalled empty set
        else:
            score = len(gold & pred) / len(gold)

        return EvaluationResult(case.id, self.name, score)
