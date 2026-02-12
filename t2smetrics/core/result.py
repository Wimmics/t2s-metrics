from dataclasses import dataclass


@dataclass
class EvaluationResult:
    query_id: str
    measure: str
    score: float
