from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.answer_set.base import AnswerSetMeasure


class AnswerSetRecall(AnswerSetMeasure):
    name = "answerset_recall"

    def compute(self, case, context):
        gold, pred = self._get_answer_sets(case, context)

        # convention: perfectly recalled empty set
        score = 1.0 if not gold else len(gold & pred) / len(gold)

        return EvaluationResult(case.id, self.name, score)
