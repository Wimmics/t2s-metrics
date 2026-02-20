import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from nltk.translate.meteor_score import meteor_score
from t2smetrics.measures.base import Measure
from t2smetrics.core.result import EvaluationResult


class Bleu(Measure):
    def __init__(self, n: int = 0, weights: tuple = None):
        """
        If n is specified, compute BLEU-n.
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


class RougeN(Measure):
    def __init__(self, n: int):
        self.n = n
        self.name = f"rouge_{n}"
        self.scorer = rouge_scorer.RougeScorer([f"rouge{n}"], use_stemmer=False)

    def compute(self, case, context=None):
        scores = self.scorer.score(case.golden.raw, case.generated.raw)
        return EvaluationResult(case.id, self.name, scores[f"rouge{self.n}"].fmeasure)


class Meteor(Measure):
    name = "meteor"

    def compute(self, case, context=None):

        nltk.download("wordnet", quiet=True)

        ref = [case.golden.tokens]
        cand = case.generated.tokens
        score = meteor_score(ref, cand)
        return EvaluationResult(case.id, self.name, score)
