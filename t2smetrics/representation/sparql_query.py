from dataclasses import dataclass
from .tokenizer import tokenize


def normalize(s: str) -> str:
    return " ".join(s.split())


@dataclass(frozen=True)
class SparqlQuery:
    raw: str

    @property
    def tokens(self) -> list[str]:
        return tokenize(self.raw)

    @property
    def normalized(self) -> str:
        return normalize(self.raw)
