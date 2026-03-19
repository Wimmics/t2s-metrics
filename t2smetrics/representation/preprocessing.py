import logging
import re
import subprocess
from collections.abc import Callable

from t2smetrics.core.eval import QueryCase
from t2smetrics.representation.sparql_query import SparqlQuery

logger = logging.getLogger(__name__)


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


def normalize_qcan(q: str) -> str:

    command = [
        "java",
        "-jar",
        "./third_party_lib/qcan-1.1-jar-with-dependencies.jar",
        "easy",
        "-q",
        f"{q}",
    ]

    # print(" ".join(command))

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.stderr:
        logger.warning(f"QCan normalization error falling back to original: {result.stderr}")
        return q

    result = result.stdout

    to_delete = [
        "usage: easy [-d] [-f <filename>] [-g] [-m] [-o <output>] [-q <query>]",
        " -d              Set to avoid writing duplicate queries in output file.",
        " -f <filename>   Filename that contains the query/queries to canonicalise.",
        " -g              Set if input is gzip file. Results will also be zipped.",
        " -m              Set to enable minimisation/leaning.",
        " -o <output>     Output file",
        " -q <query>      The query to canonicalise.",
    ]

    result = result.replace("\n".join(to_delete), "")
    return result.strip()


SP_NORMALIZER_PREPROCESSOR = Preprocessor(
    [
        normalize_whitespace,
        normalize_variables,
    ]
)

QCAN_NORMALIZER_PREPROCESSOR = Preprocessor(
    [
        normalize_qcan,
    ]
)
