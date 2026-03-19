from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu

from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.base import Metric
from t2smetrics.metrics.codebleu.dataflow import dataflow_match
from t2smetrics.metrics.codebleu.syntax import syntax_score
from t2smetrics.metrics.codebleu.weighted_bleu import weighted_precision


class CodeBLEU(Metric):
    """CodeBLEU = avg(
        BLEU,
        weighted BLEU,
        syntax score,
        dataflow score
    )
    """
    name = "codebleu"

    def compute(self, case, context=None):
        ref = [case.golden.tokens]
        cand = case.generated.tokens

        bleu = sentence_bleu(
            ref,
            cand,
            smoothing_function=SmoothingFunction().method1
        )

        w_bleu = weighted_precision(
            case.golden.tokens,
            case.generated.tokens
        )

        syntax = syntax_score(case.generated.raw)
        dataflow = dataflow_match(
            case.golden.raw,
            case.generated.raw
        )

        score = (bleu + w_bleu + syntax + dataflow) / 4.0

        return EvaluationResult(case.id, self.name, score)
