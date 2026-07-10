from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.answer_set.base import AnswerSetMeasure


class RecallQALD(AnswerSetMeasure):
    name = "recall_qald"

    def compute(self, case, context):
        gold, pred = self._get_answer_sets(case, context)

        if gold is None or pred is None:
            return EvaluationResult(case.id, self.name, 0.0)

        if len(gold) == 0 and len(pred) == 0:
            return EvaluationResult(case.id, self.name, 1.0)

        if len(gold) > 0 and len(pred) == 0:
            return EvaluationResult(case.id, self.name, 0.0)

        tp = len(gold & pred)
        fn = len(gold - pred)

        recall = tp / (tp + fn) if (tp + fn) else 0

        return EvaluationResult(case.id, self.name, recall)
