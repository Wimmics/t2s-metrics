from dataclasses import dataclass


@dataclass
class EvaluationResult:
    id: str
    measure: str
    score: float
