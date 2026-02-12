from collections import defaultdict
from typing import Iterable

from t2smetrics.core.result import EvaluationResult


class MeanAggregator:
    def aggregate(self, results: Iterable[EvaluationResult]):
        buckets = defaultdict(list)
        for r in results:
            buckets[r.measure].append(r.score)

        return {
            measure: sum(scores) / len(scores)
            for measure, scores in buckets.items()
        }
