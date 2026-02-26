import re
from typing import Callable

from t2smetrics.core.dataset import QueryCase
from t2smetrics.representation.sparql_query import SparqlQuery


class Preprocessor:
    def __init__(self, steps: list[Callable[[str], str]]):
        self.steps = steps

    def apply(self, case: QueryCase) -> QueryCase:

        for step in self.steps:
            processed_generated = step(case.generated.raw)
            processed_golden = step(case.golden.raw)

        processed_case = QueryCase(
            id=case.id,
            golden=SparqlQuery(processed_golden),
            generated=SparqlQuery(processed_generated),
            order_matters=case.order_matters,
        )
        return processed_case


def normalize_whitespace(q: str) -> str:
    return " ".join(q.split())


def normalize_variables(q: str) -> str:
    variables = {}
    counter = 0

    def repl(match):
        nonlocal counter
        var = match.group(0)
        if var not in variables:
            variables[var] = f"?v{counter}"
            counter += 1
        return variables[var]

    return re.sub(r"\?[a-zA-Z_]\w*", repl, q)


def normalize_mask_iris(q: str) -> str:
    return re.sub(r"<[^>]+>", "<IRI>", q)


SP_NORMALIZER_PREPROCESSOR = Preprocessor(
    [
        normalize_whitespace,
        normalize_variables,
    ]
)
