from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationResult:
    id: str
    measure: str
    score: float
