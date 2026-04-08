import os
from typing import Literal

import nltk
from loguru import logger
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer

from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.base import Metric
from t2smetrics.representation.preprocessing import (
    QCAN_NORMALIZER_PREPROCESSOR,
    QCAN_NORMALIZER_PREPROCESSOR_STRICT,
    SP_NORMALIZER_PREPROCESSOR,
    QCanCanonicalizationError,
    qcan_library_path,
)


class Bleu(Metric):
    def __init__(self, n: int = 0, weights: tuple = None):
        """If n is specified, compute BLEU-n.
        If n=0, compute cumulative BLEU with the provided weights or default to BLEU-4.
        """
        if n < 0:
            raise ValueError("n should be a non-negative integer.")

        if n != 0:
            if weights is not None:
                raise ValueError("If n is specified, weights should not be provided.")
            else:
                # If n is specified, compute specific BLEU-n
                self.weights = tuple(1 if i == n - 1 else 0 for i in range(n))
        else:
            if weights is None:
                # Default to cumulative BLEU-4
                self.weights = (0.25, 0.25, 0.25, 0.25)
            else:
                self.weights = weights

        self.name = "bleu"

    def compute(self, case, context=None):
        ref = [case.golden.tokens]
        cand = case.generated.tokens
        score = sentence_bleu(
            ref,
            cand,
            weights=self.weights,
            smoothing_function=SmoothingFunction().method4,
        )
        return EvaluationResult(case.id, self.name, score)


class SPBleu(Bleu):
    def __init__(self, n: int = 0, weights: tuple = None):
        super().__init__(n, weights)
        self.name = "sp-bleu"
        self.preprocessor = SP_NORMALIZER_PREPROCESSOR

    def compute(self, case, context=None):
        return super().compute(case, context)


class QCanBleu(Bleu):
    def __init__(
        self,
        n: int = 0,
        weights: tuple = None,
        calculation_type: Literal["strict", "flex"] = "strict",
    ):
        super().__init__(n, weights)
        if calculation_type not in {"strict", "flex"}:
            raise ValueError("calculation_type must be either 'strict' or 'flex'.")
        self.name = "qcan-bleu-" + calculation_type
        if calculation_type == "strict":
            self.preprocessor = QCAN_NORMALIZER_PREPROCESSOR_STRICT
        else:
            self.preprocessor = QCAN_NORMALIZER_PREPROCESSOR
        self.check_library_exists()
        self.calculation_type = calculation_type

    def run(self, case, context=None):
        try:
            return super().run(case, context)
        except QCanCanonicalizationError as error:
            logger.warning(
                f"QCan canonicalization failed in strict mode for case {case.id}. Returning 0.0. Error: {error}"
            )
            return EvaluationResult(case.id, self.name, 0.0)

    def check_library_exists(self):
        if not os.path.isfile(qcan_library_path):
            logger.error(
                f"QCan library not found at {qcan_library_path}. Please ensure the JAR file is present. You can download it from https://github.com/Wimmics/t2s-metrics/tree/main/third_party_lib"
            )
            raise FileNotFoundError(
                f"QCan library not found at {qcan_library_path}. Please ensure the JAR file is present. You can download it from https://github.com/Wimmics/t2s-metrics/tree/main/third_party_lib"
            )

    def compute(self, case, context=None):
        return super().compute(case, context)


class RougeN(Metric):
    def __init__(self, n: int):
        self.n = n
        self.name = f"rouge_{n}"
        self.scorer = rouge_scorer.RougeScorer([f"rouge{n}"], use_stemmer=False)

    def compute(self, case, context=None):
        scores = self.scorer.score(case.golden.raw, case.generated.raw)
        return EvaluationResult(case.id, self.name, scores[f"rouge{self.n}"].fmeasure)


class Meteor(Metric):
    name = "meteor"

    def compute(self, case, context=None):

        nltk.download("wordnet", quiet=True)

        ref = [case.golden.tokens]
        cand = case.generated.tokens
        score = meteor_score(ref, cand)
        return EvaluationResult(case.id, self.name, score)
