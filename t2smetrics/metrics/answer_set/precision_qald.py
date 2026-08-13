from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.answer_set.base import AnswerSetMeasure


class PrecisionQALD(AnswerSetMeasure):
    name = "precision_qald"

    def compute(self, case, context):
        gold, pred = self._get_answer_sets(case, context)

        if gold is None or pred is None:
            return EvaluationResult(case.id, self.name, 0.0)

        if len(gold) == 0 and len(pred) == 0:
            return EvaluationResult(case.id, self.name, 1.0)

        if len(gold) > 0 and len(pred) == 0:
            return EvaluationResult(case.id, self.name, 1.0)

        tp = len(gold & pred)
        fp = len(pred - gold)

        precision = tp / (tp + fp) if (tp + fp) else 0

        return EvaluationResult(case.id, self.name, precision)
