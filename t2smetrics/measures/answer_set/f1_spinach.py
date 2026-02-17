from t2smetrics.measures.answer_set.base import AnswerSetMeasure
from t2smetrics.core.result import EvaluationResult


class F1Spinach(AnswerSetMeasure):
    name = "f1_spinach"

    # TODO : check the official implementation at https://github.com/stanford-oval/spinach/blob/8bb2d9cfa7f54b7b63ba5e6acd8264fdb7f8ecf9/eval.py#L108 

    def compute(self, case, context):
        gold, pred = self._get_answer_lists(case, context)

        if not self._validate(gold, pred):
            return EvaluationResult(case.id, self.name, 0.0)

        gold = set(tuple(row) for row in gold or [])
        pred = set(tuple(row[:len(next(iter(gold)))]) for row in pred or [])

        tp = len(gold & pred)
        fp = len(pred - gold)
        fn = len(gold - pred)

        precision = tp / (tp + fp) if (tp + fp) else 0
        recall = tp / (tp + fn) if (tp + fn) else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

        return EvaluationResult(case.id, self.name, f1)
