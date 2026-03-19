from collections import defaultdict
from collections.abc import Iterable

from t2smetrics.core.result import EvaluationResult


class MeanAggregator:
    def aggregate(self, results: Iterable[EvaluationResult]):
        buckets = defaultdict(list)
        for r in results:
            buckets[r.metric].append(r.score)

        return {
            metric: sum(scores) / len(scores)
            for metric, scores in buckets.items()
        }
