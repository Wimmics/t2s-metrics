from t2smetrics.measures.answer_set.base import AnswerSetMeasure
from t2smetrics.core.result import EvaluationResult


class PrecisionQALD(AnswerSetMeasure):
    name = "precision_qald"

    def compute(self, case, context):
        gold, pred = self._get_answer_sets(case, context)

        if not self._validate(gold, pred):
            return EvaluationResult(case.id, self.name, 0.0)

        tp = len(gold & pred)
        fp = len(pred - gold)

        precision = tp / (tp + fp) if (tp + fp) else 0

        return EvaluationResult(case.id, self.name, precision)
