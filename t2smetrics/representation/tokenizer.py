import re

TOKEN_PATTERN = re.compile(r"""
    [A-Za-z_][A-Za-z0-9_]*   # identifiers
  | \?[A-Za-z_][A-Za-z0-9_]* # variables
  | <[^>]*>                 # IRIs
  | "[^"]*"                 # strings
  | [{}();.,]               # punctuation
""", re.VERBOSE)


def tokenize(sparql: str) -> list[str]:
    return TOKEN_PATTERN.findall(sparql)
