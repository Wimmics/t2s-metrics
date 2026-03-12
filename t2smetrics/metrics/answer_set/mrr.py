from t2smetrics.core.context import EvaluationContext
from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.answer_set.base import AnswerSetMeasure


class MRR(AnswerSetMeasure):
    name = "mrr"

    def compute(self, case, context: EvaluationContext = None):
        gold, pred = self._get_answer_lists(case, context)

        if not self._validate(gold, pred):
            return EvaluationResult(case.id, self.name, 0.0)

        for i, ans in enumerate(pred):
            if ans in gold:
                return EvaluationResult(case.id, self.name, 1.0 / (i + 1))

        return EvaluationResult(case.id, self.name, 0.0)
