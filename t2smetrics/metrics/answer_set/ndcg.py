import math

from t2smetrics.core.eval import QueryCase
from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.answer_set.base import AnswerSetMeasure


def dcg(relevances):
    return sum(rel / math.log2(i + 2) for i, rel in enumerate(relevances))


class NDCG(AnswerSetMeasure):
    name = "ndcg"

    def compute(self, case: QueryCase, context=None) -> EvaluationResult:

        gold, pred = self._get_answer_lists(case, context)

        if not self._validate(gold, pred):
            return EvaluationResult(case.id, self.name, 0.0)

        relevances = [1 if a in gold else 0 for a in pred]
        actual_dcg = dcg(relevances)

        ideal_relevances = [1] * len(gold)

        if len(ideal_relevances) < len(pred):
            ideal_relevances += [0] * (len(pred) - len(ideal_relevances))

        ideal_dcg = dcg(ideal_relevances)

        score = 0.0 if ideal_dcg == 0 else actual_dcg / ideal_dcg

        return EvaluationResult(case.id, self.name, score)
