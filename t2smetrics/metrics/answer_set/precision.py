from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.answer_set.base import AnswerSetMeasure


class AnswerSetPrecision(AnswerSetMeasure):
    name = "answerset_precision"

    def compute(self, case, context):
        gold, pred = self._get_answer_sets(case, context)

        score = 0.0 if not pred else len(gold & pred) / len(pred)

        return EvaluationResult(case.id, self.name, score)
