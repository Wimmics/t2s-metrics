from abc import ABC, abstractmethod

from t2smetrics.core.eval import QueryCase
from t2smetrics.core.result import EvaluationResult
from t2smetrics.representation.preprocessing import Preprocessor


class Metric(ABC):
    name: str
    requires_execution = False
    requires_llm = False
    requires_ranking = False
    preprocessor: Preprocessor = None

    def run(self, case: QueryCase, context=None) -> EvaluationResult:
        if self.preprocessor:
            case = self.preprocessor.apply(case)
        return self.compute(case, context)

    @abstractmethod
    def compute(self, case: QueryCase, context=None) -> EvaluationResult:
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}()"
