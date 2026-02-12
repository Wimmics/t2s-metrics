from t2smetrics.core.context import EvaluationContext
from t2smetrics.measures.answer_set.base import AnswerSetMeasure
from t2smetrics.core.result import EvaluationResult


class PrecisionAt1(AnswerSetMeasure):
    name = "p@1"

    def compute(self, case, context: EvaluationContext = None):
        gold, pred = self._get_answer_lists(case, context)

        if not self._validate(gold, pred):
            score = 0.0
        else:
            score = float(pred[0] in gold)

        return EvaluationResult(case.id, self.name, score)
