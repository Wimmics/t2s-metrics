import re
import subprocess
from collections.abc import Callable

from loguru import logger

from t2smetrics.core.eval import QueryCase
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


qcan_library_path = "./third_party_lib/qcan-1.1-jar-with-dependencies.jar"


class QCanCanonicalizationError(RuntimeError):
    pass


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


def normalize_qcan(q: str, fallback_to_original: bool = True) -> str:

    command = [
        "java",
        "-jar",
        qcan_library_path,
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
        if fallback_to_original:
            logger.warning(
                f"QCan normalization error falling back to original: {result.stderr}"
            )
            return q
        raise QCanCanonicalizationError(result.stderr.strip())

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


def normalize_qcan_strict(q: str) -> str:
    return normalize_qcan(q, fallback_to_original=False)


def _outside(q, func):
    """Apply func only to the parts of q outside IRIs and string literals."""
    # IRIs and string literals are "shielded": transformations never touch them.
    SHIELD = re.compile(r'(<[^>]*>|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')')

    parts = SHIELD.split(q)
    return "".join(func(p) if i % 2 == 0 else p for i, p in enumerate(parts))


def normalize_naive_can(q: str) -> str:
    KEYWORDS = {
        "SELECT",
        "CONSTRUCT",
        "ASK",
        "DESCRIBE",
        "WHERE",
        "FILTER",
        "OPTIONAL",
        "UNION",
        "GRAPH",
        "SERVICE",
        "BIND",
        "VALUES",
        "ORDER",
        "GROUP",
        "BY",
        "HAVING",
        "LIMIT",
        "OFFSET",
        "DISTINCT",
        "REDUCED",
        "NOT",
        "EXISTS",
        "MINUS",
        "AS",
        "IN",
        "FROM",
        "NAMED",
        "UNDEF",
        "TRUE",
        "FALSE",
    }

    q = _outside(q, lambda p: re.sub(r"#[^\n]*", "", p))  # 1. strip comments
    prefixes = dict(re.findall(r"(?i)\bPREFIX\s+([\w.-]*):\s*<([^>]*)>", q))
    q = re.sub(r"(?i)\b(?:PREFIX\s+[\w.-]*:\s*<[^>]*>|BASE\s*<[^>]*>)", " ", q)

    def expand(m):  # 2. pref:local -> <iri>
        return f"<{prefixes[m[1]]}{m[2]}>" if m[1] in prefixes else m[0]

    q = _outside(q, lambda p: re.sub(r"([\w.-]*):([\w.-]*)", expand, p))
    q = _outside(
        q,
        lambda p: re.sub(  # 3. uppercase keywords
            r"\b[a-zA-Z]+\b",
            lambda m: m[0].upper() if m[0].upper() in KEYWORDS else m[0],
            p,
        ),
    )
    renaming = {}  # 4. ?foo/$foo -> ?v1...

    def rename(m):
        return renaming.setdefault(m[1], f"?v{len(renaming) + 1}")

    q = _outside(q, lambda p: re.sub(r"[?$](\w+)", rename, p))
    q = _outside(
        q, lambda p: re.sub(r"\s*([{}()\[\],;])\s*", r" \1 ", p)
    )  # 5. token spacing
    q = _outside(
        q, lambda p: re.sub(r"\s*\.(\s|$)", r" . ", p)
    )  # triple-final dots only
    return re.sub(r"\s+", " ", q).strip()  # 6. collapse whitespace


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

QCAN_NORMALIZER_PREPROCESSOR_STRICT = Preprocessor(
    [
        normalize_qcan_strict,
    ]
)

NAIVE_CAN_PREPROCESSOR = Preprocessor(
    [
        normalize_naive_can,
    ]
)
