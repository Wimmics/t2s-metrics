from Levenshtein import distance as levenshtein
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import jaccard_score
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

from t2smetrics.core.result import EvaluationResult
from t2smetrics.metrics.base import Metric


class LevenshteinDistance(Metric):
    name = "levenshtein"

    def compute(self, case, context=None):
        dist = levenshtein(case.golden.raw, case.generated.raw)
        max_len = max(len(case.golden.raw), len(case.generated.raw))

        # both empty → identical
        score = 1.0 if max_len == 0 else 1 - dist / max_len

        return EvaluationResult(case.id, self.name, score)


class JaccardSimilarity(Metric):
    name = "jaccard"

    def compute(self, case, context=None):
        v = CountVectorizer(binary=True)
        X = v.fit_transform([case.golden.raw, case.generated.raw]).toarray()
        score = jaccard_score(X[0], X[1])
        return EvaluationResult(case.id, self.name, score)


class CosineSimilarity(Metric):
    name = "cosine_sim"

    def compute(self, case, context=None):
        v = CountVectorizer()
        X = v.fit_transform([case.golden.raw, case.generated.raw])
        score = cosine_similarity(X[0], X[1])[0][0]
        return EvaluationResult(case.id, self.name, score)


class EuclideanDistance(Metric):
    name = "euclidean"

    def compute(self, case, context=None):
        v = CountVectorizer(binary=True)
        X = v.fit_transform([case.golden.raw, case.generated.raw]).toarray()
        distance = euclidean_distances([X[0]], [X[1]])[0][0]
        score = 1 / (1 + distance)
        return EvaluationResult(case.id, self.name, score)
