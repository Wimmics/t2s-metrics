from t2smetrics.measures.answer_set.base import AnswerSetMeasure
from t2smetrics.core.result import EvaluationResult


class PrecisionQALD(AnswerSetMeasure):
    name = "precision_qald"

    def compute(self, case, context):
        gold, pred = self._get_answer_sets(case, context)

        if gold is not None and len(gold) > 0 and pred is not None and len(pred) == 0:
            return EvaluationResult(case.id, self.name, 1.0)

        tp = len(gold & pred)
        fp = len(pred - gold)

        precision = tp / (tp + fp) if (tp + fp) else 0

        return EvaluationResult(case.id, self.name, precision)
