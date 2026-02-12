from t2smetrics.core.context import EvaluationContext
from t2smetrics.core.result import EvaluationResult
from t2smetrics.measures.answer_set.base import AnswerSetMeasure


class HitAt5(AnswerSetMeasure):
    name = "hit@5"

    def compute(self, case, context: EvaluationContext = None):
        gold, pred = self._get_answer_lists(case, context)

        if not self._validate(gold, pred):
            return EvaluationResult(case.id, self.name, 0.0)

        top5 = pred[:5]
        score = float(any(a in gold for a in top5))
        return EvaluationResult(case.id, self.name, score)
