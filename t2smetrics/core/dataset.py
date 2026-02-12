import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from t2smetrics.representation.sparql_query import SparqlQuery


@dataclass
class QueryCase:
    id: str
    golden: SparqlQuery
    generated: SparqlQuery
    order_matters: bool


class JsonlDataset:
    def __init__(self, path: str):
        self.path = Path(path)

    def __iter__(self) -> Iterator[QueryCase]:
        with self.path.open() as f:
            for line in f:
                row = json.loads(line)
                yield QueryCase(
                    id=row["id"],
                    golden=SparqlQuery(row["golden"]),
                    generated=SparqlQuery(row["generated"]),
                    order_matters=row["order_matters"],
                )

    def __len__(self) -> int:
        with self.path.open() as f:
            return sum(1 for _ in f)
