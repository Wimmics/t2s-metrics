import re
from typing import Callable


class Preprocessor:
    def __init__(self, steps: list[Callable[[str], str]]):
        self.steps = steps

    def apply(self, query: str) -> str:
        for step in self.steps:
            query = step(query)
        return query


def normalize_whitespace(q: str) -> str:
    return " ".join(q.split()).lower()


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


def normalize_iris(q: str) -> str:
    return re.sub(r"<[^>]+>", "<IRI>", q)


CANONICAL_PREPROCESSOR = Preprocessor([
    normalize_whitespace,
    normalize_variables,
    normalize_iris
])
