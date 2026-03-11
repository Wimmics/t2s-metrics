from t2smetrics.metrics.answer_set.base import AnswerSetMeasure
from t2smetrics.core.result import EvaluationResult


class AnswerSetPrecision(AnswerSetMeasure):
    name = "answerset_precision"

    def compute(self, case, context):
        gold, pred = self._get_answer_sets(case, context)

        if not pred:
            score = 0.0
        else:
            score = len(gold & pred) / len(pred)

        return EvaluationResult(case.id, self.name, score)
