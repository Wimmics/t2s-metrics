from t2smetrics.measures.answer_set.base import AnswerSetMeasure
from t2smetrics.core.result import EvaluationResult


class RecallQALD(AnswerSetMeasure):
    name = "recall_qald"

    def compute(self, case, context):
        gold, pred = self._get_answer_sets(case, context)

        if not self._validate(gold, pred):
            return EvaluationResult(case.id, self.name, 0.0)

        tp = len(gold & pred)
        fn = len(gold - pred)

        recall = tp / (tp + fn) if (tp + fn) else 0

        return EvaluationResult(case.id, self.name, recall)