from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.answer_set.base import AnswerSetMeasure


class AnswerSetPrecision(AnswerSetMeasure):
    name = "answerset_precision"

    def compute(self, case, context):
        gold, pred = self._get_answer_sets(case, context)

        # Handle None cases
        if gold is None or pred is None:
            return EvaluationResult(case.id, self.name, 0.0)

        if len(gold) == 0 and len(pred) == 0:
            return EvaluationResult(case.id, self.name, 1.0)

        if len(gold) > 0 and len(pred) == 0:
            # Check QALD Precision for the other logic: if the gold is non-empty and the prediction is empty, precision is 1.0
            return EvaluationResult(case.id, self.name, 0.0)

        # Normal case
        tp = len(gold & pred)
        fp = len(pred - gold)
        precision = tp / (tp + fp)

        return EvaluationResult(case.id, self.name, precision)
