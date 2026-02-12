import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from nltk.translate.meteor_score import meteor_score
from t2smetrics.measures.base import Measure
from t2smetrics.core.result import EvaluationResult


class Bleu4(Measure):
    name = "bleu_4"

    def compute(self, case, context=None):
        ref = [case.golden.tokens]
        cand = case.generated.tokens
        score = sentence_bleu(
            ref,
            cand,
            weights=(0.25, 0.25, 0.25, 0.25),
            smoothing_function=SmoothingFunction().method1
        )
        return EvaluationResult(case.id, self.name, score)


class RougeN(Measure):
    def __init__(self, n: int):
        self.n = n
        self.name = f"rouge_{n}"
        self.scorer = rouge_scorer.RougeScorer([f"rouge{n}"], use_stemmer=False)

    def compute(self, case, context=None):
        scores = self.scorer.score(
            case.golden.raw,
            case.generated.raw
        )
        return EvaluationResult(case.id, self.name, scores[f"rouge{self.n}"].fmeasure)


class Meteor(Measure):
    name = "meteor"

    def compute(self, case, context=None):

        nltk.download("wordnet", quiet=True)

        ref = [case.golden.tokens]
        cand = case.generated.tokens
        score = meteor_score(
            ref,
            cand
        )
        return EvaluationResult(case.id, self.name, score)
