from collections import Counter

from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.base import Metric
from t2smetrics.representation.preprocessing import SP_NORMALIZER_PREPROCESSOR


def precision_recall_f1(gold, pred):
    tp = sum((gold & pred).values())
    fp = sum(pred.values()) - tp
    fn = sum(gold.values()) - tp

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    return precision, recall, f1


class TokenPrecision(Metric):
    name = "token_precision"

    def compute(self, case, context=None):
        p, _, _ = precision_recall_f1(
            Counter(case.golden.tokens), Counter(case.generated.tokens)
        )
        return EvaluationResult(case.id, self.name, p)


class TokenRecall(Metric):
    name = "token_recall"

    def compute(self, case, context=None):
        _, r, _ = precision_recall_f1(
            Counter(case.golden.tokens), Counter(case.generated.tokens)
        )
        return EvaluationResult(case.id, self.name, r)


class TokenF1(Metric):
    name = "token_f1"

    def compute(self, case, context=None):
        _, _, f1 = precision_recall_f1(
            Counter(case.golden.tokens), Counter(case.generated.tokens)
        )
        return EvaluationResult(case.id, self.name, f1)


class SPF1(TokenF1):

    def __init__(self, context=None):
        self.name = "sp-f1"
        self.preprocessor = SP_NORMALIZER_PREPROCESSOR

    def compute(self, case, context=None):
        return super().compute(case, context)
