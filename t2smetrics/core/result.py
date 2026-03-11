from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class EvaluationResult:
    id: str
    metric: str
    score: float

    def to_dict(self):
        return asdict(self)
