import json
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from SPARQLWrapper import QueryResult

from t2smetrics.representation.sparql_query import SparqlQuery

_NOT_CACHED = object()


@dataclass
class QueryCase:
    id: str
    golden: SparqlQuery
    generated: SparqlQuery
    order_matters: bool
    golden_response: "QueryResult.ConvertResult" = _NOT_CACHED
    generated_response: "QueryResult.ConvertResult" = _NOT_CACHED
    is_uri_hallicinated_map: dict[str, bool] = field(default_factory=dict)


class JsonlEval:
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
