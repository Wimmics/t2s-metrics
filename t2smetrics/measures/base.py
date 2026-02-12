from abc import ABC, abstractmethod
from t2smetrics.core.result import EvaluationResult
from t2smetrics.core.dataset import QueryCase


class Measure(ABC):
    name: str
    requires_execution = False
    requires_llm = False
    requires_ranking = False

    @abstractmethod
    def compute(self, case: QueryCase, context=None) -> EvaluationResult:
        pass
