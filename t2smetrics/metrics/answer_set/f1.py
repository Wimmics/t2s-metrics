from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.answer_set.base import AnswerSetMeasure


class AnswerSetF1(AnswerSetMeasure):
    name = "answerset_f1"

    def compute(self, case, context):
        gold, pred = self._get_answer_sets(case, context)

        if not self._validate(gold, pred):
            return EvaluationResult(case.id, self.name, 0.0)

        tp = len(gold & pred)
        fp = len(pred - gold)
        fn = len(gold - pred)

        precision = tp / (tp + fp) if (tp + fp) else 0
        recall = tp / (tp + fn) if (tp + fn) else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

        return EvaluationResult(case.id, self.name, f1)
